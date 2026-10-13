/// <reference path="../pb_data/types.d.ts" />
//
// BK-015 (RFC-LAB-000-015 / Spike D77 / Spec ask-the-portfolio):
// Grounded AI Assistant "Ask-the-Portfolio" Endpoint (POST /api/ask)
//
// Architecture & Contract:
// 1. Accepts POST /api/ask with { question: string }
// 2. Structured questions (counts, status filters, ownership, metadata) -> answered
//    deterministically from data/*.json with ZERO LLM calls, cited to the source row(s) (R2.1, R2.3).
// 3. Narrative questions -> section-anchored retrieval over repo docs by section/sprint-id anchor
//    (R2.2, D77 revision), calling configured LLM via $http.send with fail-closed prompt (R2.3, R3.2).
// 4. Boundary & fail-closed: public-read boundary only (R3.1); missing facts or absent key fail-closed
//    without 500 or fabrication (R3.2, R5.1).
// 5. Evaluative / judgment questions labelled [Advisory] (R3.3).
// 6. Config-driven model seam (R4.1); key from Railway env only, never logged or returned (R4.2).

routerAdd("POST", "/api/ask", function(e) {
  try {
    // --- Helper Functions Scoped to Handler ---

    function readTextFile(path) {
      try {
        var bytes = $os.readFile(path);
        if (bytes) {
          return toString(bytes);
        }
      } catch (_) {}
      return null;
    }

    function readJsonFile(path) {
      var text = readTextFile(path);
      if (!text) return null;
      try {
        return JSON.parse(text);
      } catch (_) {
        return null;
      }
    }

    function isStopword(w) {
      var sw = [
        "what", "which", "where", "when", "about", "tell", "show", "give", "please",
        "with", "from", "that", "this", "have", "were", "been", "their", "there",
        "project", "projects", "portfolio", "initiative", "initiatives", "cetana", "labs",
        "question", "answer", "data", "info", "information"
      ];
      return sw.indexOf(w) !== -1;
    }

    function isPrivateBoundaryQuery(q) {
      var forbidden = [
        "_superusers",
        "pb_admin_password",
        "admin_password",
        "superuser password",
        "private token",
        "railway_token",
        "secret_key"
      ];
      for (var i = 0; i < forbidden.length; i++) {
        if (q.indexOf(forbidden[i]) !== -1) return true;
      }
      return false;
    }

    function getResolvedPaths() {
      var envData = $os.getenv("DATA_DIR");
      var envDocs = $os.getenv("DOCS_DIR");
      var envRoot = $os.getenv("REPO_ROOT");

      var repoRoot = envRoot || "";
      if (!repoRoot) {
        var candidates = [
          __hooks + "/../../..",
          __hooks + "/../..",
          __hooks + "/..",
          ".",
          "/pb"
        ];
        for (var i = 0; i < candidates.length; i++) {
          try {
            if ($os.stat(candidates[i] + "/CHANGELOG.md")) {
              repoRoot = candidates[i];
              break;
            }
          } catch (_) {}
        }
      }

      var dataDir = envData || "";
      if (!dataDir) {
        var dataCandidates = [
          repoRoot ? repoRoot + "/data" : "",
          __hooks + "/../../../data",
          __hooks + "/../../data",
          __hooks + "/../data",
          __hooks + "/data",
          "./data",
          "/pb/data"
        ];
        for (var j = 0; j < dataCandidates.length; j++) {
          if (!dataCandidates[j]) continue;
          try {
            if ($os.stat(dataCandidates[j] + "/portfolio.json")) {
              dataDir = dataCandidates[j];
              break;
            }
          } catch (_) {}
        }
      }

      var docsDir = envDocs || "";
      if (!docsDir) {
        var docsCandidates = [
          repoRoot ? repoRoot + "/docs" : "",
          __hooks + "/../../../docs",
          __hooks + "/../../docs",
          __hooks + "/../docs",
          __hooks + "/docs",
          "./docs",
          "/pb/docs"
        ];
        for (var k = 0; k < docsCandidates.length; k++) {
          if (!docsCandidates[k]) continue;
          try {
            if ($os.stat(docsCandidates[k] + "/README.md")) {
              docsDir = docsCandidates[k];
              break;
            }
          } catch (_) {}
        }
      }

      return {
        repoRoot: repoRoot || (__hooks + "/../../.."),
        dataDir: dataDir || (__hooks + "/data"),
        docsDir: docsDir || (__hooks + "/docs")
      };
    }

    function loadPortfolioData(app, paths) {
      var portfolio = readJsonFile(paths.dataDir + "/portfolio.json");
      var status = readJsonFile(paths.dataDir + "/status.json");
      var users = readJsonFile(paths.dataDir + "/users.json");

      // Fallback to SQLite collections if data files not directly reachable on disk
      if ((!portfolio || portfolio.length === 0) && app) {
        try {
          var records = app.findRecordsByFilter("projects", "1=1", "lab_id", 100, 0);
          portfolio = records.map(function(r) {
            return {
              id: r.get("lab_id"),
              slug: r.get("slug"),
              name: r.get("name"),
              descriptor: r.get("descriptor"),
              archetype: r.get("archetype"),
              owner_id: r.get("owner"),
              repo_url: r.get("repo_url"),
              reference_url: r.get("reference_url"),
              dev_environment: r.get("dev_environment"),
              status_source: r.get("status_source")
            };
          });
        } catch (_) {}
      }

      if ((!users || users.length === 0) && app) {
        try {
          var uRecords = app.findRecordsByFilter("users", "1=1", "seed_id", 100, 0);
          users = uRecords.map(function(r) {
            return {
              id: r.get("seed_id") || r.id,
              name: r.get("name"),
              github_handle: r.get("github_handle"),
              role: r.get("role"),
              org: r.get("org"),
              active: r.get("active")
            };
          });
        } catch (_) {}
      }

      return {
        portfolio: portfolio || [],
        status: status || [],
        users: users || []
      };
    }

    function matchProjectFromQuery(q, portfolio) {
      // 1. Direct ID match (LAB-XXX)
      var idMatch = q.match(/\b(lab-\d{3})\b/i);
      if (idMatch) {
        var id = idMatch[1].toUpperCase();
        for (var i = 0; i < portfolio.length; i++) {
          if (portfolio[i].id === id) return portfolio[i];
        }
      }

      // 2. Slug match
      for (var j = 0; j < portfolio.length; j++) {
        var p = portfolio[j];
        if (p.slug && q.indexOf(p.slug.toLowerCase()) !== -1) {
          return p;
        }
      }

      // 3. Name keywords
      var nameMap = [
        { key: "nexus pulse", id: "LAB-003" },
        { key: "ammas", id: "LAB-001" },
        { key: "aamas", id: "LAB-001" },
        { key: "wrenai", id: "LAB-002" },
        { key: "zerobea", id: "LAB-004" },
        { key: "beacon", id: "LAB-005" },
        { key: "cetana", id: "LAB-000" }
      ];

      for (var k = 0; k < nameMap.length; k++) {
        if (q.indexOf(nameMap[k].key) !== -1) {
          for (var l = 0; l < portfolio.length; l++) {
            if (portfolio[l].id === nameMap[k].id) return portfolio[l];
          }
        }
      }

      return null;
    }

    function handleStructuredQuery(rawQuestion, q, data) {
      var portfolio = data.portfolio;
      var status = data.status;
      var users = data.users;

      // Intent A: Count Active Projects
      // e.g. "how many active projects?", "how many projects are active?", "count active projects"
      if (
        /how\s+many(\s+projects)?\s+are\s+active/i.test(q) ||
        /how\s+many\s+active(\s+projects)?/i.test(q) ||
        /count\s+active(\s+projects)?/i.test(q) ||
        /active\s+projects\s+count/i.test(q) ||
        /number\s+of\s+active\s+projects/i.test(q) ||
        /which\s+projects\s+are\s+active/i.test(q) ||
        /what\s+projects\s+are\s+active/i.test(q)
      ) {
        var activeProjects = status.filter(function(s) {
          return !s.is_completed && !s.is_onboarding_pending;
        });
        var activeList = activeProjects.map(function(s) {
          var proj = null;
          for (var i = 0; i < portfolio.length; i++) {
            if (portfolio[i].id === s.id) { proj = portfolio[i]; break; }
          }
          return proj ? (s.id + " (" + proj.name + ")") : s.id;
        });

        return {
          answer: "There are " + activeProjects.length + " active projects in the portfolio: " + activeList.join(" and ") + ".",
          citations: ["data/status.json", "data/portfolio.json"],
          grounded: true
        };
      }

      // Intent B: At-Risk / Blocked Projects
      // e.g. "which projects are at risk?", "are any projects blocked?", "what is at risk?"
      if (
        /at[\s-]risk/i.test(q) ||
        /\bblocked\b/i.test(q) ||
        /any\s+blockers/i.test(q)
      ) {
        var atRisk = status.filter(function(s) {
          var h = String(s.health || "");
          return h.indexOf("At Risk") !== -1 || h.indexOf("Blocked") !== -1;
        });

        if (atRisk.length === 0) {
          return {
            answer: "There are currently no projects at risk or blocked in the portfolio.",
            citations: ["data/status.json"],
            grounded: true
          };
        }

        var details = atRisk.map(function(s) {
          return s.id + ": " + s.health + " (blockers: " + (s.blockers || "None") + ")";
        });
        return {
          answer: "The following projects are at risk or blocked: " + details.join("; ") + ".",
          citations: ["data/status.json"],
          grounded: true
        };
      }

      // Intent C: Ownership
      // e.g. "who owns LAB-003?", "who is the owner of LAB-000?", "who owns ammas?"
      if (
        /who\s+(owns|leads|is\s+(the\s+)?owner\s+of|is\s+leading)\b/i.test(q) ||
        /\bowner\s+of\b/i.test(q) ||
        /\blead\s+of\b/i.test(q)
      ) {
        var proj = matchProjectFromQuery(q, portfolio);
        if (!proj) {
          return {
            answer: "Project not found in the portfolio data.",
            citations: ["data/portfolio.json"],
            grounded: false
          };
        }

        var owner = null;
        for (var uIdx = 0; uIdx < users.length; uIdx++) {
          if (users[uIdx].id === proj.owner_id) { owner = users[uIdx]; break; }
        }
        var ownerName = owner ? owner.name : "Unknown";
        return {
          answer: proj.id + " (" + proj.name + ") is owned by " + ownerName + ".",
          citations: ["data/portfolio.json (" + proj.id + ")", "data/users.json (" + proj.owner_id + ")"],
          grounded: true
        };
      }

      // Intent D: Evaluative Judgment / "in trouble" (R3.3 Advisory labelling)
      // e.g. "is LAB-003 in trouble?", "is any project in trouble?"
      if (
        /\bin\s+trouble\b/i.test(q) ||
        /\bfailing\b/i.test(q)
      ) {
        var jProj = matchProjectFromQuery(q, portfolio);
        if (jProj) {
          var s = null;
          for (var sIdx = 0; sIdx < status.length; sIdx++) {
            if (status[sIdx].id === jProj.id) { s = status[sIdx]; break; }
          }
          if (s) {
            var isHealthy = s.health.indexOf("Blocked") === -1 && s.health.indexOf("At Risk") === -1;
            var assessment = isHealthy ? "There is no indication that the project is in trouble." : "The project has recorded risks or blockers.";
            var metricsStr = (s.metrics && s.metrics.length > 0) ? (" Verified metrics: " + s.metrics.join("; ") + ".") : "";
            return {
              answer: "[Advisory] Based on data/status.json, " + jProj.id + " (" + jProj.name + ") is currently '" + s.health + "' with blockers: '" + (s.blockers || "None") + "'." + metricsStr + " " + assessment,
              citations: ["data/status.json (" + jProj.id + ")"],
              grounded: true
            };
          }
        }

        // Portfolio-wide evaluation
        var blocked = status.filter(function(st) {
          return st.health.indexOf("Blocked") !== -1 || st.health.indexOf("At Risk") !== -1;
        });
        if (blocked.length === 0) {
          return {
            answer: "[Advisory] Based on data/status.json, all portfolio initiatives are currently on track or completed. No projects are in trouble or blocked.",
            citations: ["data/status.json"],
            grounded: true
          };
        }
      }

      // Intent E: Project Metadata (Repo URL, Archetype, Dev Environment, Descriptor)
      // e.g. "what is the repo url for LAB-003?", "what is the archetype of LAB-002?"
      var mProj = matchProjectFromQuery(q, portfolio);
      if (mProj) {
        if (/repo(\s+url)?|repository|github\s+url|source\s+code/i.test(q)) {
          var url = mProj.repo_url || mProj.reference_url || "No repository URL registered";
          return {
            answer: "The repository URL for " + mProj.id + " (" + mProj.name + ") is " + url + ".",
            citations: ["data/portfolio.json (" + mProj.id + ")"],
            grounded: true
          };
        }
        if (/archetype/i.test(q)) {
          return {
            answer: "The archetype for " + mProj.id + " (" + mProj.name + ") is '" + mProj.archetype + "'.",
            citations: ["data/portfolio.json (" + mProj.id + ")"],
            grounded: true
          };
        }
        if (/dev(elopment)?\s+environment|where\s+does.*run/i.test(q)) {
          return {
            answer: "The development environment for " + mProj.id + " (" + mProj.name + ") is '" + mProj.dev_environment + "'.",
            citations: ["data/portfolio.json (" + mProj.id + ")"],
            grounded: true
          };
        }
        if (/descriptor/i.test(q)) {
          return {
            answer: "The descriptor for " + mProj.id + " (" + mProj.name + ") is '" + mProj.descriptor + "'.",
            citations: ["data/portfolio.json (" + mProj.id + ")"],
            grounded: true
          };
        }
        if (/status\s+source/i.test(q)) {
          return {
            answer: "The status source for " + mProj.id + " (" + mProj.name + ") is '" + mProj.status_source + "'.",
            citations: ["data/portfolio.json (" + mProj.id + ")"],
            grounded: true
          };
        }
      }

      // Intent F: Total / Completed / Onboarding Counts
      if (/how\s+many\s+total\s+projects/i.test(q) || /total\s+projects/i.test(q)) {
        return {
          answer: "There are " + portfolio.length + " total projects registered in the portfolio.",
          citations: ["data/portfolio.json"],
          grounded: true
        };
      }
      if (/how\s+many\s+completed\s+projects/i.test(q) || /completed\s+projects/i.test(q)) {
        var completed = status.filter(function(s) { return s.is_completed; });
        var compIds = completed.map(function(s) { return s.id; }).join(", ");
        return {
          answer: "There are " + completed.length + " completed projects in the portfolio: " + compIds + ".",
          citations: ["data/status.json"],
          grounded: true
        };
      }
      if (/how\s+many\s+onboarding\s+pending/i.test(q) || /onboarding\s+pending\s+projects/i.test(q)) {
        var pending = status.filter(function(s) { return s.is_onboarding_pending; });
        var pendIds = pending.map(function(s) { return s.id; }).join(", ");
        return {
          answer: "There are " + pending.length + " projects pending onboarding: " + pendIds + ".",
          citations: ["data/status.json"],
          grounded: true
        };
      }

      return null;
    }

    function parseMarkdownIntoSections(sourceRel, text) {
      var lines = text.split("\n");
      var sections = [];
      var currentHeading = "Overview";
      var currentLines = [];

      for (var i = 0; i < lines.length; i++) {
        var line = lines[i];
        var m = line.match(/^(#{1,3})\s+(.+)$/);
        if (m) {
          if (currentLines.length > 0) {
            sections.push({
              source: sourceRel,
              heading: currentHeading,
              content: currentLines.join("\n").trim()
            });
            currentLines = [];
          }
          currentHeading = m[2].trim();
        } else {
          currentLines.push(line);
        }
      }

      if (currentLines.length > 0) {
        sections.push({
          source: sourceRel,
          heading: currentHeading,
          content: currentLines.join("\n").trim()
        });
      }

      return sections;
    }

    function getDocSections(paths) {
      var sections = [];
      var root = paths.repoRoot;

      var filesToIndex = [
        { rel: "CHANGELOG.md", abs: root + "/CHANGELOG.md" },
        { rel: "SPRINT_TRACKER.md", abs: root + "/SPRINT_TRACKER.md" },
        { rel: "README.md", abs: root + "/README.md" },
        { rel: "projects/LAB-000-cetana-labs/README.md", abs: root + "/projects/LAB-000-cetana-labs/README.md" },
        { rel: "projects/LAB-000-cetana-labs/STATUS.md", abs: root + "/projects/LAB-000-cetana-labs/STATUS.md" },
        { rel: "projects/LAB-001-ammas/README.md", abs: root + "/projects/LAB-001-ammas/README.md" },
        { rel: "projects/LAB-001-ammas/STATUS.md", abs: root + "/projects/LAB-001-ammas/STATUS.md" },
        { rel: "projects/LAB-002-wrenai-eval/README.md", abs: root + "/projects/LAB-002-wrenai-eval/README.md" },
        { rel: "projects/LAB-002-wrenai-eval/STATUS.md", abs: root + "/projects/LAB-002-wrenai-eval/STATUS.md" },
        { rel: "projects/LAB-003-nexus-pulse/README.md", abs: root + "/projects/LAB-003-nexus-pulse/README.md" },
        { rel: "projects/LAB-003-nexus-pulse/STATUS.md", abs: root + "/projects/LAB-003-nexus-pulse/STATUS.md" },
        { rel: "projects/LAB-004-zerobea-ai/README.md", abs: root + "/projects/LAB-004-zerobea-ai/README.md" },
        { rel: "projects/LAB-004-zerobea-ai/STATUS.md", abs: root + "/projects/LAB-004-zerobea-ai/STATUS.md" },
        { rel: "projects/LAB-005-nexus-beacon/README.md", abs: root + "/projects/LAB-005-nexus-beacon/README.md" },
        { rel: "projects/LAB-005-nexus-beacon/STATUS.md", abs: root + "/projects/LAB-005-nexus-beacon/STATUS.md" },
        { rel: "docs/rfc/RFC-LAB-000-015-ai-assistant.md", abs: paths.docsDir + "/rfc/RFC-LAB-000-015-ai-assistant.md" },
        { rel: "docs/guides/developer-guide.md", abs: paths.docsDir + "/guides/developer-guide.md" },
        { rel: "docs/guides/project-owner-guide.md", abs: paths.docsDir + "/guides/project-owner-guide.md" },
        { rel: "docs/governance/DECISION-JOURNAL.md", abs: paths.docsDir + "/governance/DECISION-JOURNAL.md" },
        { rel: "docs/governance/ai-collaboration-model.md", abs: paths.docsDir + "/governance/ai-collaboration-model.md" }
      ];

      for (var i = 0; i < filesToIndex.length; i++) {
        var f = filesToIndex[i];
        var text = readTextFile(f.abs);
        if (text) {
          var parsed = parseMarkdownIntoSections(f.rel, text);
          for (var j = 0; j < parsed.length; j++) {
            sections.push(parsed[j]);
          }
        }
      }

      return sections;
    }

    function retrieveDocSections(rawQuestion, q, paths) {
      var corpus = getDocSections(paths);
      if (!corpus || corpus.length === 0) return null;

      var sprintMatch = q.match(/sprint[-\s]?(\d+)/i);
      var requestedSprintNum = sprintMatch ? sprintMatch[1] : (q.indexOf("last sprint") !== -1 ? "12" : null);

      var labMatch = q.match(/lab-(\d{3})/i);
      var requestedLabId = labMatch ? ("LAB-" + labMatch[1]) : null;

      var bkMatch = q.match(/bk-(\d{3})/i);
      var requestedBkId = bkMatch ? ("BK-" + bkMatch[1]) : null;

      var queryTokens = q
        .replace(/[^a-z0-9\s]/g, " ")
        .split(/\s+/)
        .filter(function(t) { return t.length > 3 && !isStopword(t); });

      var scored = [];

      for (var i = 0; i < corpus.length; i++) {
        var sec = corpus[i];
        var score = 0;
        var hLower = sec.heading.toLowerCase();
        var cLower = sec.content.toLowerCase();
        var sLower = sec.source.toLowerCase();

        // 1. Exact Sprint Anchor Match (D77 revision: selects the archive section)
        if (requestedSprintNum) {
          var sprintPattern = new RegExp("sprint\\s*" + requestedSprintNum + "\\b", "i");
          if (sprintPattern.test(hLower)) {
            score += 150;
          } else if (sprintPattern.test(cLower)) {
            score += 40;
          }
        }

        // 2. Exact LAB ID Anchor Match
        if (requestedLabId) {
          if (sLower.indexOf(requestedLabId.toLowerCase()) !== -1) {
            score += 120;
          }
          var labPattern = new RegExp("\\b" + requestedLabId.toLowerCase() + "\\b", "i");
          if (labPattern.test(hLower)) {
            score += 80;
          }
          if (labPattern.test(cLower)) {
            score += 30;
          }
        }

        // 3. Exact BK ID Anchor Match
        if (requestedBkId) {
          var bkPattern = new RegExp("\\b" + requestedBkId.toLowerCase() + "\\b", "i");
          if (bkPattern.test(hLower)) {
            score += 100;
          }
          if (bkPattern.test(cLower)) {
            score += 30;
          }
        }

        // 4. Token Overlap in Heading (+15) and Body (+2)
        for (var t = 0; t < queryTokens.length; t++) {
          var tok = queryTokens[t];
          if (hLower.indexOf(tok) !== -1) score += 15;
          if (cLower.indexOf(tok) !== -1) score += 2;
        }

        if (score > 15) {
          scored.push({ sec: sec, score: score });
        }
      }

      scored.sort(function(a, b) { return b.score - a.score; });

      if (scored.length === 0 || scored[0].score < 30) return null;

      var selected = [];
      var citations = [];
      var totalLength = 0;
      var maxChars = 5000;

      for (var k = 0; k < scored.length && selected.length < 3; k++) {
        var item = scored[k].sec;
        if (totalLength + item.content.length > maxChars && selected.length > 0) {
          break;
        }
        selected.push(item);
        totalLength += item.content.length;
        if (citations.indexOf(item.source) === -1) {
          citations.push(item.source);
        }
      }

      return {
        sections: selected,
        citations: citations
      };
    }

    function callGroundedLLM(rawQuestion, retrieved, app, apiKey) {
      var model = "gpt-4o-mini";
      var endpoint = "https://api.openai.com/v1/chat/completions";

      if (app) {
        try {
          var modelRec = app.findFirstRecordByFilter("settings", "key = 'llm_model'");
          if (modelRec && modelRec.get("value")) model = String(modelRec.get("value")).trim();
        } catch (_) {}

        try {
          var endRec = app.findFirstRecordByFilter("settings", "key = 'llm_endpoint'");
          if (endRec && endRec.get("value")) endpoint = String(endRec.get("value")).trim();
        } catch (_) {}
      }

      var envModel = $os.getenv("LLM_MODEL");
      if (envModel) model = envModel.trim();
      var envEndpoint = $os.getenv("LLM_ENDPOINT");
      if (envEndpoint) endpoint = envEndpoint.trim();

      var contextBlocks = retrieved.sections.map(function(s) {
        return "[Source: " + s.source + " — " + s.heading + "]\n" + s.content;
      });
      var contextText = contextBlocks.join("\n\n---\n\n");

      var systemPrompt = "You answer ONLY from the provided context about the Cetana Labs portfolio. Ground every claim in the context and cite the source doc. If the answer is not in the context, say so — never invent. If the question asks for an opinion or evaluative judgment, start your response with '[Advisory]'.";

      var userPrompt = "Context:\n---\n" + contextText + "\n---\n\nQuestion: " + rawQuestion;

      try {
        var res = $http.send({
          url: endpoint,
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + apiKey
          },
          body: JSON.stringify({
            model: model,
            messages: [
              { role: "system", content: systemPrompt },
              { role: "user", content: userPrompt }
            ],
            temperature: 0,
            max_tokens: 500
          }),
          timeout: 30
        });

        if (res.statusCode !== 200) {
          return {
            answer: "AI assistant is currently unavailable (model service returned " + res.statusCode + ").",
            citations: [],
            grounded: false
          };
        }

        var resJson = res.json;
        if (!resJson || !resJson.choices || !resJson.choices[0] || !resJson.choices[0].message) {
          return {
            answer: "AI assistant is currently unavailable (invalid response format from model).",
            citations: [],
            grounded: false
          };
        }

        var answer = String(resJson.choices[0].message.content || "").trim();

        var refusalPatterns = [
          "not in the context",
          "not mentioned in the context",
          "not present in the context",
          "context does not contain",
          "context does not mention",
          "context does not provide",
          "cannot be found in the provided context"
        ];

        var grounded = true;
        var lowerAns = answer.toLowerCase();
        for (var r = 0; r < refusalPatterns.length; r++) {
          if (lowerAns.indexOf(refusalPatterns[r]) !== -1) {
            grounded = false;
            break;
          }
        }

        return {
          answer: answer,
          citations: grounded ? retrieved.citations : [],
          grounded: grounded
        };
      } catch (err) {
        return {
          answer: "AI assistant is currently unavailable (connection timeout or error).",
          citations: [],
          grounded: false
        };
      }
    }

    // --- 1. Request Validation (R1.1, R1.3) ---
    var body = null;
    try {
      var info = e.requestInfo();
      if (info && info.body) {
        body = info.body;
      }
    } catch (_) {}

    if (!body || typeof body !== "object") {
      try {
        var raw = toString(e.request.body);
        if (raw) {
          body = JSON.parse(raw);
        }
      } catch (_) {}
    }

    var rawQuestion = (body && typeof body.question === "string") ? body.question.trim() : "";
    if (!rawQuestion) {
      return e.json(400, { error: "Missing or empty 'question' in request body" });
    }

    // --- 2. Data Resolution (Paths & Fallbacks) ---
    var paths = getResolvedPaths();
    var data = loadPortfolioData(e.app, paths);

    // Normalize query for intent classification
    var q = rawQuestion.toLowerCase();

    // --- 3. Boundary & Secret Protection (R3.1, R4.2) ---
    if (isPrivateBoundaryQuery(q)) {
      return e.json(200, {
        answer: "This information is private and not accessible through the public assistant interface.",
        citations: [],
        grounded: false
      });
    }

    // --- 4. Structured Router (R2.1 — ZERO LLM CALL) ---
    var structuredResult = handleStructuredQuery(rawQuestion, q, data);
    if (structuredResult) {
      return e.json(200, structuredResult);
    }

    // --- 5. Narrative Path: Section-Anchored Retrieval (R2.2 — D77 revision) ---
    var retrieved = retrieveDocSections(rawQuestion, q, paths);

    if (!retrieved || retrieved.sections.length === 0) {
      // Fail-closed when no grounded documentation matches the query (R3.2)
      return e.json(200, {
        answer: "This fact is not present in the portfolio data or documentation.",
        citations: [],
        grounded: false
      });
    }

    // --- 6. Grounded LLM Call (R2.3, R3.2, R4.1, R4.2, R5.1) ---
    var apiKey = $os.getenv("LLM_API_KEY");
    if (!apiKey) {
      // Fail-closed on infra: no model key -> graceful unavailable message (R5.1, V6)
      return e.json(200, {
        answer: "AI assistant is currently unavailable for narrative questions (no LLM key configured). Structured portfolio queries remain fully available.",
        citations: [],
        grounded: false
      });
    }

    var llmResult = callGroundedLLM(rawQuestion, retrieved, e.app, apiKey);
    return e.json(200, llmResult);
  } catch (err) {
    console.log("[ask.pb.js] ERROR:", err);
    return e.json(500, { error: String(err) });
  }
});
