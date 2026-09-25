import { loadProjects } from '$lib/data';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ fetch }) => {
  const projects = await loadProjects(fetch);
  return { projects };
};
