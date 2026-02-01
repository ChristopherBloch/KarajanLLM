const fs = require("fs");

function patchProviderUtils() {
  const filePath = "/usr/local/lib/node_modules/openclaw/dist/utils/provider-utils.js";
  let text = fs.readFileSync(filePath, "utf8");
  let updated = text;

  if (!updated.includes('normalized === "litellm"')) {
    updated = updated.replace(
      'normalized === "ollama" ||',
      'normalized === "ollama" ||\n        normalized === "litellm" ||\n        normalized.startsWith("litellm/") ||'
    );
  } else if (!updated.includes('normalized.startsWith("litellm/")')) {
    updated = updated.replace(
      'normalized === "litellm" ||',
      'normalized === "litellm" ||\n        normalized.startsWith("litellm/") ||'
    );
  }

  if (updated !== text) {
    fs.writeFileSync(filePath, updated);
    return true;
  }
  return false;
}

function patchReasoningTags() {
  const filePath = "/usr/local/lib/node_modules/openclaw/dist/shared/text/reasoning-tags.js";
  let text = fs.readFileSync(filePath, "utf8");
  let updated = text;

  if (!updated.includes("const hasFinalTag = FINAL_TAG_RE.test(cleaned);") && updated.includes("let cleaned = text;")) {
    updated = updated.replace(
      "let cleaned = text;\n    if (FINAL_TAG_RE.test(cleaned)) {",
      "let cleaned = text;\n    const hasFinalTag = FINAL_TAG_RE.test(cleaned);\n    if (hasFinalTag) {"
    );
  }

  if (!updated.includes("let unclosedThinking = \"\";")) {
    updated = updated.replace(
      "let inThinking = false;\n",
      "let inThinking = false;\n    let unclosedThinking = \"\";\n"
    );
  }

  if (!updated.includes("unclosedThinking = cleaned.slice(lastIndex);")) {
    updated = updated.replace(
      "    if (!inThinking || mode === \"preserve\") {",
      "    if (inThinking) {\n        unclosedThinking = cleaned.slice(lastIndex);\n    }\n    if (!inThinking || mode === \"preserve\") {"
    );
  }

  if (!updated.includes("const trimmedResult = applyTrim(result, trimMode);") && updated.includes("return applyTrim(result, trimMode);")) {
    updated = updated.replace(
      "    return applyTrim(result, trimMode);\n}",
      "    const trimmedResult = applyTrim(result, trimMode);\n    if (!hasFinalTag && trimmedResult === \"\" && unclosedThinking) {\n        return applyTrim(unclosedThinking, trimMode);\n    }\n    return trimmedResult;\n}"
    );
  }

  if (updated !== text) {
    fs.writeFileSync(filePath, updated);
    return true;
  }
  return false;
}

let changed = false;
changed = patchProviderUtils() || changed;
changed = patchReasoningTags() || changed;

if (changed) {
  console.log("openclaw patch applied");
} else {
  console.log("openclaw patch already applied");
}
