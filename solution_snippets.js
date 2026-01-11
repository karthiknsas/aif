
// --- SYSTEM PROMPT BUILDER (Data-Aware Version) ---
function buildSystemPrompt(req) {
    const dC = APP.data.length ? `COLS: ${JSON.stringify(APP.cols)}` : "";
    return `
SYSTEM: JS Code Generator.
${dC}
USER: "${req}"

STRICT RULES:
1. FORMAT (NO JSON):
<<<TARGET>>>
{target_id}
<<<DESCRIPTION>>>
{text}
<<<JAVASCRIPT>>>
{code}
<<<END>>>

2. LOGIC:
- CHARTS: Use ApexCharts. Destroy old: APP.charts.c1?.destroy(). New: APP.charts.c1 = new ApexCharts(document.querySelector("#canvas_1"), options); APP.charts.c1.render().
- TEXT: Update document.getElementById('AI_SUMMARY').innerHTML.
- THEME: Update document.getElementById('GEN_CSS').innerHTML.

3. DATA RULES:
- DO NOT hallucinate values.
- DO NOT use hardcoded numbers (like [10, 20]).
- YOU MUST write JS code to transform 'APP.data'.
- Example: data: APP.data.map(r => r.Sales)

EXAMPLE:
<<<TARGET>>>
canvas_1
<<<DESCRIPTION>>>
Sales by Region
<<<JAVASCRIPT>>>
APP.charts.c1?.destroy();
// Process Data
const seriesData = APP.data.map(r => r.Sales);
const catData = APP.data.map(r => r.Region);

var opt = {
  series: [{ data: seriesData }],
  xaxis: { categories: catData },
  chart: { type: 'bar' }
};
APP.charts.c1 = new ApexCharts(document.querySelector("#canvas_1"), opt);
APP.charts.c1.render();
<<<END>>>
`;
}

// --- EXECUTION FUNCTION ---
async function GEN_EXECUTE() {
    const req = document.getElementById("user_input").value.trim();
    if (!req) return;

    addLog("🟢 REQUEST: " + req, "info");
    addMsg("user", req);
    document.getElementById("user_input").value = "";

    const prompt = buildSystemPrompt(req);

    try {
        setChatState("disabled");
        addMsg("system", "Thinking...");

        const res = await callAI([{ role: "user", content: prompt }]);
        const reply = res.choices[0].message.content.trim();

        addLog("ai-code", reply);

        // --- CUSTOM PARSER (Robust Regex) ---
        // 1. Matches <<<TARGET>>> blocks even if wrapped in markdown like ```text ... ```
        const regex = /<<<TARGET>>>\s*(\S+)\s*<<<DESCRIPTION>>>\s*([\s\S]*?)\s*<<<JAVASCRIPT>>>\s*([\s\S]*?)\s*<<<END>>>/gi;

        let match;
        let foundAny = false;

        while ((match = regex.exec(reply)) !== null) {
            foundAny = true;
            const targetId = match[1].trim();
            const description = match[2].trim();
            const code = match[3].trim();

            addMsg("ai", `<strong>${targetId}:</strong> ${description}`);

            try {
                const fn = new Function("APP", "document", "ApexCharts", code);
                fn(APP, document, ApexCharts);
                addLog("✅ Executed on " + targetId, "success");
            } catch (err) {
                addLog("❌ Exec Error (" + targetId + "): " + err.message, "error");
            }
        }

        if (!foundAny) {
            // Fallback: Check if response has code but missing delimiters (sometimes happens)
             addLog("⚠️ No valid block found. Response: " + reply.substring(0, 100) + "...", "warn");
             addMsg("ai", reply);
        }

    } catch (e) {
        addLog("❌ ERROR: " + e.message, "error");
        addMsg("system", "Error: " + e.message);
    } finally {
        setChatState("ready");
    }
}
