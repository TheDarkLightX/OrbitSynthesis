-- Convert the manuscript's math-like inline code spans into real TeX math.
-- Paths, hashes, commands, solver verdicts, and source identifiers remain code.

local literal_code = {
  ["NO_HIT"] = true,
  ["UNKNOWN"] = true,
  ["UNSAT"] = true,
  ["QF_BV"] = true,
  ["OriginalSignature"] = true,
  ["decide"] = true,
  ["python -O"] = true,
  ["native_decide"] = true,
  ["sorry"] = true,
  ["admit"] = true,
  ["axiom"] = true,
  ["unsafe"] = true,
}

local function is_hash(value)
  return value:match("^[0-9a-f]+$") and #value >= 32
end

local function is_path(value)
  if value:find("\\", 1, true) then
    return true
  end
  for _, suffix in ipairs({".md", ".py", ".json", ".lean", ".olean", ".sh"}) do
    if value:sub(-#suffix) == suffix then
      return true
    end
  end
  for _, prefix in ipairs({
    "research/", "runs/", "notes/", "paper/", "src/", "experiments/",
    "lanes/", "audits/", "formal/", "program-vector-optimization/",
  }) do
    if value:sub(1, #prefix) == prefix then
      return true
    end
  end
  return false
end

local function is_code(value)
  if literal_code[value] then
    return true
  end
  if is_hash(value) then
    return true
  end
  if is_path(value) then
    return true
  end
  return false
end

local function matching_paren(value, open_at)
  local depth = 0
  for index = open_at, #value do
    local char = value:sub(index, index)
    if char == "(" then
      depth = depth + 1
    elseif char == ")" then
      depth = depth - 1
      if depth == 0 then
        return index
      end
    end
  end
  return nil
end

local function replace_words(value)
  value = value:gsub("!=", "\\ne ")
  value = value:gsub("<=", "\\le ")
  value = value:gsub(">=", "\\ge ")
  value = value:gsub("%-%>", "\\to ")
  value = value:gsub("%.%.%.", "\\ldots ")
  value = value:gsub("%*", "\\mathbin{\\cdot}")
  value = value:gsub("%f[%a]Theta%f[%A]", "\\Theta")
  value = value:gsub("%f[%a]Omega%f[%A]", "\\Omega")
  value = value:gsub("%f[%a]Delta%f[%A]", "\\Delta")
  value = value:gsub("%f[%a]CT%f[%A]", "\\mathrm{CT}")
  value = value:gsub("%f[%a]alpha%f[%A]", "\\alpha")
  value = value:gsub("%f[%a]sigma%f[%A]", "\\sigma")
  value = value:gsub("%f[%a]iota%f[%A]", "\\iota")
  value = value:gsub("%f[%a]sum%f[%A]", "\\sum")
  value = value:gsub("%f[%a]product%f[%A]", "\\prod")
  value = value:gsub("%f[%a]max%f[%A]", "\\max")
  value = value:gsub("%f[%a]log%f[%A]", "\\log")
  value = value:gsub("%f[%a]exp%f[%A]", "\\exp")
  value = value:gsub("%f[%a]size%f[%A]", "\\operatorname{size}")
  value = value:gsub("%f[%a]depth%f[%A]", "\\operatorname{depth}")
  value = value:gsub("%f[%a]EqSel%f[%A]", "\\operatorname{EqSel}")
  value = value:gsub("%f[%a]Glue%f[%A]", "\\operatorname{Glue}")
  value = value:gsub("%f[%a]Dec%f[%A]", "\\operatorname{Dec}")
  value = value:gsub("%f[%a]Sel%f[%A]", "\\operatorname{Sel}")
  value = value:gsub("%f[%a]physical%f[%A]", "\\text{physical}")
  value = value:gsub("%f[%a]otherwise%f[%A]", "\\text{otherwise}")
  value = value:gsub("%f[%a]when%f[%A]", "\\text{when}")
  value = value:gsub("%f[%a]for%f[%A]", "\\text{for}")
  value = value:gsub("%f[%a]if%f[%A]", "\\text{if}")
  value = value:gsub("%s+in%s+", " \\in ")
  value = value:gsub("%s+xor%s+", " \\mathbin{\\mathrm{xor}} ")
  value = value:gsub("%f[%a]not%s+", "\\neg ")
  value = value:gsub("%f[%a]square%f[%A]", "\\square")
  return value
end

local function convert_segment(value)
  local output = {}
  local index = 1
  local functions = {
    {name = "ceil", left = "\\lceil ", right = " \\rceil"},
    {name = "floor", left = "\\lfloor ", right = " \\rfloor"},
    {name = "sqrt", left = "\\sqrt{", right = "}"},
    {name = "bar", left = "\\overline{", right = "}"},
  }

  while index <= #value do
    local handled = false

    for _, fn in ipairs(functions) do
      local prefix = fn.name .. "("
      if value:sub(index, index + #prefix - 1) == prefix then
        local open_at = index + #fn.name
        local close_at = matching_paren(value, open_at)
        if close_at then
          local inner = value:sub(open_at + 1, close_at - 1)
          table.insert(output, fn.left .. convert_segment(inner) .. fn.right)
          index = close_at + 1
          handled = true
          break
        end
      end
    end

    if not handled then
      local char = value:sub(index, index)
      if (char == "^" or char == "_") and value:sub(index + 1, index + 1) == "(" then
        local close_at = matching_paren(value, index + 1)
        if close_at then
          local inner = value:sub(index + 2, close_at - 1)
          table.insert(output, char .. "{" .. convert_segment(inner) .. "}")
          index = close_at + 1
          handled = true
        end
      end
    end

    if not handled then
      table.insert(output, value:sub(index, index))
      index = index + 1
    end
  end

  return table.concat(output)
end

local function wrap_long_scripts(value)
  value = value:gsub("_([A-Za-z][A-Za-z0-9]*)", function(script)
    if #script == 1 then
      return "_" .. script
    end
    return "_{\\mathrm{" .. script .. "}}"
  end)
  value = value:gsub("%^([A-Za-z][A-Za-z0-9]*)", function(script)
    if #script == 1 then
      return "^" .. script
    end
    return "^{\\mathrm{" .. script .. "}}"
  end)
  return value
end

local function to_math(value)
  value = value:gsub("{", "@@SETL@@"):gsub("}", "@@SETR@@")

  -- A function-valued exponent needs to be grouped before ordinary parsing.
  value = value:gsub("%^ceil%(([^()]*)%)", "^{\\lceil %1 \\rceil}")
  value = value:gsub("%^floor%(([^()]*)%)", "^{\\lfloor %1 \\rfloor}")
  value = value:gsub("%^sqrt%(([^()]*)%)", "^{\\sqrt{%1}}")

  value = convert_segment(value)
  value = replace_words(value)
  value = wrap_long_scripts(value)
  value = value:gsub("@@SETL@@", "\\{"):gsub("@@SETR@@", "\\}")
  return value
end

function Code(element)
  if is_hash(element.text) then
    return pandoc.RawInline("latex", "\\texttt{\\seqsplit{" .. element.text .. "}}")
  end
  if is_path(element.text) then
    return pandoc.RawInline("latex", "\\path{" .. element.text .. "}")
  end
  if is_code(element.text) then
    return element
  end
  return pandoc.Math("InlineMath", to_math(element.text))
end

local function trim(value)
  return value:match("^%s*(.-)%s*$")
end

local function is_equation_block(value)
  local found = false
  for line in (value .. "\n"):gmatch("(.-)\n") do
    line = trim(line)
    if line ~= "" then
      local has_relation = line:find("=", 1, true)
        or line:find("<", 1, true)
        or line:find(">", 1, true)
        or line:find("->", 1, true)
      if not has_relation then
        return false
      end
      found = true
    end
  end
  return found
end

function CodeBlock(element)
  if not is_equation_block(element.text) then
    return element
  end

  local rows = {}
  for line in (element.text .. "\n"):gmatch("(.-)\n") do
    line = trim(line)
    if line ~= "" then
      table.insert(rows, to_math(line))
    end
  end

  local separator = " " .. string.char(92) .. string.char(92) .. "\n"
  local latex = "\\[\n\\begin{aligned}\n"
    .. table.concat(rows, separator)
    .. "\n\\end{aligned}\n\\]"
  return pandoc.RawBlock("latex", latex)
end
