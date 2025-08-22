export const lcaRoute = (
  projectId: string,
  leaf: 'scope' | 'lci' | 'lcia' | 'interpretation' | 'report'
) => `/lca/projects/${projectId}/${leaf}`;
