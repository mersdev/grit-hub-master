const GENERAL_SKILLS = new Set([
  "deep-research",
  "memory-recall",
  "memory-save",
  "learning-tracker",
  "code-review",
]);

function normalize(text) {
  return String(text || "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, " ")
    .trim();
}

function tokenize(text) {
  return [...new Set(normalize(text).split(/\s+/).filter(Boolean))];
}

function titleCase(text) {
  return String(text || "")
    .split(/\s+/)
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

function canonicalSlug(text) {
  return normalize(text).replace(/\s+/g, "-");
}

function isGenericSkill(skill) {
  return GENERAL_SKILLS.has(skill);
}

function hasDedicatedSkill(agent) {
  const skills = Array.isArray(agent?.skills) ? agent.skills : [];
  return skills.some((skill) => !isGenericSkill(skill));
}

function suggestDedicatedSkillSlug(agent) {
  const source = [
    agent?.name,
    agent?.raw_name,
    agent?.description,
    ...(agent?.keywords || []),
    ...(agent?.capabilities || []),
  ].join(" ");

  const stop = new Set([
    "agent",
    "predictor",
    "expert",
    "assistant",
    "friendly",
    "data",
    "analysis",
    "analyze",
    "predict",
    "prediction",
    "match",
    "team",
    "teams",
    "use",
    "using",
    "skill",
    "skills",
    "generate",
    "creation",
    "create",
    "build",
    "help",
  ]);

  const tokens = tokenize(source).filter((token) => !stop.has(token));
  const picked = tokens.slice(0, 4);
  const slug = canonicalSlug(picked.join(" "));
  return slug ? `${slug}-analysis` : "custom-domain-analysis";
}

function skillScopeWarning(agent) {
  if (!agent?.buildable) return null;
  if (String(agent.role || "").toLowerCase() !== "everyone") return null;
  const skills = Array.isArray(agent.skills) ? agent.skills : [];
  if (skills.length === 0) return null;
  if (hasDedicatedSkill(agent)) return null;
  if (!skills.every(isGenericSkill)) return null;

  const suggestion = suggestDedicatedSkillSlug(agent);
  return {
    agentName: agent.name || agent.slug,
    suggestion,
    message: `Agent "${agent.name || agent.slug}" only uses generic skills. Consider a dedicated skill like "${suggestion}" instead of reusing general-purpose skills alone.`,
  };
}

module.exports = {
  GENERAL_SKILLS,
  hasDedicatedSkill,
  isGenericSkill,
  skillScopeWarning,
  suggestDedicatedSkillSlug,
};
