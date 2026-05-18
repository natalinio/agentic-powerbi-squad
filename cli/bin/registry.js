/**
 * Component registry — all installable agents, skills, and references.
 */

const COMPONENT_REGISTRY = [
  // ─── Agents ───────────────────────────────────────────────────────────────────
  {
    id: 'agent:delivery-lead',
    type: 'agent',
    name: 'Delivery Lead',
    description: 'End-to-end workflow orchestration and project management',
    sourcePath: 'agents/delivery-lead.agent.md',
    targetPath: 'agents/delivery-lead.agent.md',
    dependencies: ['skill:workflow-orchestration'],
    tags: ['orchestration', 'management']
  },
  {
    id: 'agent:business-data-analyst',
    type: 'agent',
    name: 'Business Data Analyst',
    description: 'Requirements analysis, KPI extraction, and business rules',
    sourcePath: 'agents/business-data-analyst.agent.md',
    targetPath: 'agents/business-data-analyst.agent.md',
    dependencies: ['skill:requirements-analysis'],
    tags: ['analysis', 'requirements']
  },
  {
    id: 'agent:pbi-semantic-model',
    type: 'agent',
    name: 'PBI Semantic Model',
    description: 'Logical model design, TMDL authoring, DAX measures',
    sourcePath: 'agents/pbi-semantic-model.agent.md',
    targetPath: 'agents/pbi-semantic-model.agent.md',
    dependencies: ['skill:logical-model', 'skill:physical-model-tmdl', 'skill:dax-development'],
    tags: ['modeling', 'tmdl', 'dax']
  },
  {
    id: 'agent:pbi-report',
    type: 'agent',
    name: 'PBI Report',
    description: 'Report design and PBIR implementation',
    sourcePath: 'agents/pbi-report.agent.md',
    targetPath: 'agents/pbi-report.agent.md',
    dependencies: ['skill:report-design', 'skill:report-implementation'],
    tags: ['report', 'pbir', 'visuals']
  },
  {
    id: 'agent:pbi-qa',
    type: 'agent',
    name: 'PBI QA',
    description: 'Quality assurance, validation, and testing',
    sourcePath: 'agents/pbi-qa.agent.md',
    targetPath: 'agents/pbi-qa.agent.md',
    dependencies: ['skill:code-review', 'skill:functional-testing', 'skill:report-quality-validation'],
    tags: ['qa', 'testing', 'validation']
  },
  {
    id: 'agent:data-generator',
    type: 'agent',
    name: 'Data Generator',
    description: 'Mock data generation for local development',
    sourcePath: 'agents/data-generator.agent.md',
    targetPath: 'agents/data-generator.agent.md',
    dependencies: ['skill:mock-data-generation'],
    tags: ['data', 'mock', 'csv']
  },

  // ─── Skills ───────────────────────────────────────────────────────────────────
  {
    id: 'skill:code-review',
    type: 'skill',
    name: 'Code Review',
    description: 'TMDL quality validation, DAX BPA compliance, naming conventions',
    sourcePath: 'skills/code-review',
    targetPath: 'skills/code-review',
    tags: ['qa', 'validation']
  },
  {
    id: 'skill:dax-development',
    type: 'skill',
    name: 'DAX Development',
    description: 'DAX measure authoring patterns, optimization, and pitfalls',
    sourcePath: 'skills/dax-development',
    targetPath: 'skills/dax-development',
    tags: ['dax', 'measures']
  },
  {
    id: 'skill:deneb-visuals',
    type: 'skill',
    name: 'Deneb Visuals',
    description: 'Vega and Vega-Lite custom visuals for Power BI',
    sourcePath: 'skills/deneb-visuals',
    targetPath: 'skills/deneb-visuals',
    tags: ['visuals', 'deneb', 'vega']
  },
  {
    id: 'skill:functional-testing',
    type: 'skill',
    name: 'Functional Testing',
    description: 'Automated DAX measure testing against expected values',
    sourcePath: 'skills/functional-testing',
    targetPath: 'skills/functional-testing',
    tags: ['testing', 'qa']
  },
  {
    id: 'skill:html-visuals',
    type: 'skill',
    name: 'HTML Visuals',
    description: 'Full-frame HTML/SVG via DAX for htmlContent custom visual',
    sourcePath: 'skills/html-visuals',
    targetPath: 'skills/html-visuals',
    tags: ['visuals', 'html', 'svg']
  },
  {
    id: 'skill:logical-model',
    type: 'skill',
    name: 'Logical Model',
    description: 'Star schema design, Kimball methodology, relationship patterns',
    sourcePath: 'skills/logical-model',
    targetPath: 'skills/logical-model',
    tags: ['modeling', 'design']
  },
  {
    id: 'skill:mock-data-generation',
    type: 'skill',
    name: 'Mock Data Generation',
    description: 'Synthetic CSV dataset generation from model schema',
    sourcePath: 'skills/mock-data-generation',
    targetPath: 'skills/mock-data-generation',
    tags: ['data', 'mock']
  },
  {
    id: 'skill:physical-model-tmdl',
    type: 'skill',
    name: 'Physical Model (TMDL)',
    description: 'TMDL file generation and editing for semantic models',
    sourcePath: 'skills/physical-model-tmdl',
    targetPath: 'skills/physical-model-tmdl',
    tags: ['tmdl', 'modeling']
  },
  {
    id: 'skill:project-initialization',
    type: 'skill',
    name: 'Project Initialization',
    description: 'PBIP project scaffolding and folder structure',
    sourcePath: 'skills/project-initialization',
    targetPath: 'skills/project-initialization',
    tags: ['project', 'scaffold']
  },
  {
    id: 'skill:report-design',
    type: 'skill',
    name: 'Report Design',
    description: 'Storyboard layout, UX, information architecture, blueprint generation',
    sourcePath: 'skills/report-design',
    targetPath: 'skills/report-design',
    tags: ['report', 'design', 'ux']
  },
  {
    id: 'skill:report-implementation',
    type: 'skill',
    name: 'Report Implementation',
    description: 'PBIR page and visual JSON generation from blueprints',
    sourcePath: 'skills/report-implementation',
    targetPath: 'skills/report-implementation',
    tags: ['report', 'pbir', 'implementation']
  },
  {
    id: 'skill:report-quality-validation',
    type: 'skill',
    name: 'Report Quality Validation',
    description: 'PBIR structure validation, field binding checks, accessibility',
    sourcePath: 'skills/report-quality-validation',
    targetPath: 'skills/report-quality-validation',
    tags: ['qa', 'report', 'validation']
  },
  {
    id: 'skill:requirements-analysis',
    type: 'skill',
    name: 'Requirements Analysis',
    description: 'Functional spec analysis, KPI extraction, dimension identification',
    sourcePath: 'skills/requirements-analysis',
    targetPath: 'skills/requirements-analysis',
    tags: ['analysis', 'requirements']
  },
  {
    id: 'skill:svg-visuals',
    type: 'skill',
    name: 'SVG Visuals',
    description: 'Inline SVG micro-charts via DAX measures',
    sourcePath: 'skills/svg-visuals',
    targetPath: 'skills/svg-visuals',
    tags: ['visuals', 'svg', 'dax']
  },
  {
    id: 'skill:theme-customization',
    type: 'skill',
    name: 'Theme Customization',
    description: 'Power BI report theme creation and validation',
    sourcePath: 'skills/theme-customization',
    targetPath: 'skills/theme-customization',
    tags: ['theme', 'design']
  },
  {
    id: 'skill:workflow-orchestration',
    type: 'skill',
    name: 'Workflow Orchestration',
    description: 'End-to-end workflow state management (delivery-lead internal)',
    sourcePath: 'skills/workflow-orchestration',
    targetPath: 'skills/workflow-orchestration',
    tags: ['orchestration', 'internal']
  },

  // ─── References ───────────────────────────────────────────────────────────────
  {
    id: 'ref:naming-conventions',
    type: 'reference',
    name: 'Naming Conventions',
    description: 'Naming standards for semantic model and report objects',
    sourcePath: 'references/naming-conventions.md',
    targetPath: 'references/naming-conventions.md',
    tags: ['standards', 'naming']
  },
  {
    id: 'ref:pbip-folder-structure',
    type: 'reference',
    name: 'PBIP Folder Structure',
    description: 'PBIP workspace layout and folder conventions',
    sourcePath: 'references/pbip-folder-structure.md',
    targetPath: 'references/pbip-folder-structure.md',
    tags: ['standards', 'structure']
  },
  {
    id: 'ref:pbir-cli-integration',
    type: 'reference',
    name: 'PBIR CLI Integration',
    description: 'PBIR CLI tooling integration reference',
    sourcePath: 'references/pbir-cli-integration.md',
    targetPath: 'references/pbir-cli-integration.md',
    tags: ['tooling', 'cli']
  },
  {
    id: 'ref:security-rls',
    type: 'reference',
    name: 'Security & RLS Best Practices',
    description: 'Row-level security guidance and patterns',
    sourcePath: 'references/security-rls-best-practices.md',
    targetPath: 'references/security-rls-best-practices.md',
    tags: ['security', 'rls']
  },

  // ─── Templates ────────────────────────────────────────────────────────────────
  {
    id: 'template:base-theme',
    type: 'template',
    name: 'Base Theme (ProjectDefault)',
    description: 'Default Power BI theme template for new projects',
    sourcePath: 'templates/BaseThemes/ProjectDefault.json',
    targetPath: 'templates/BaseThemes/ProjectDefault.json',
    tags: ['theme', 'template']
  },
  {
    id: 'template:copilot-instructions',
    type: 'template',
    name: 'Copilot Instructions',
    description: 'Repository-level copilot-instructions.md for Power BI projects',
    sourcePath: 'copilot-instructions.md',
    targetPath: 'copilot-instructions.md',
    tags: ['config', 'copilot']
  }
];

function getComponentsByType(type) {
  return COMPONENT_REGISTRY.filter(c => c.type === type);
}

function getComponentById(id) {
  return COMPONENT_REGISTRY.find(c => c.id === id);
}

function findComponents(query) {
  const q = query.toLowerCase();
  return COMPONENT_REGISTRY.filter(c =>
    c.id.toLowerCase().includes(q) ||
    c.name.toLowerCase().includes(q) ||
    c.tags.some(t => t.includes(q))
  );
}

/**
 * Resolve all dependencies for a set of component IDs (recursive).
 */
function resolveDependencies(ids) {
  const resolved = new Set();
  const queue = [...ids];
  while (queue.length > 0) {
    const id = queue.pop();
    if (resolved.has(id)) continue;
    resolved.add(id);
    const comp = getComponentById(id);
    if (comp && comp.dependencies) {
      for (const dep of comp.dependencies) {
        if (!resolved.has(dep)) queue.push(dep);
      }
    }
  }
  return [...resolved];
}

module.exports = {
  COMPONENT_REGISTRY,
  getComponentsByType,
  getComponentById,
  findComponents,
  resolveDependencies
};
