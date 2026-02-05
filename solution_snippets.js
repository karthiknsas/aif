
// --- SYSTEM PROMPT BUILDER (Multi-Example Version) ---
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

2. TARGETS (CHOOSE ONE):
- 'AI_SUMMARY' (For text, answers, explanations)
- 'canvas_1' (For main chart)
- 'GEN_CSS' (For theme changes)

3. BEHAVIOR:
- General Question/Greeting -> Use 'AI_SUMMARY'. NO CHARTS.
- Visualization Request -> Use 'canvas_1'.

EXAMPLE 1 (General Chat):
<<<TARGET>>>
AI_SUMMARY
<<<DESCRIPTION>>>
Answering user question
<<<JAVASCRIPT>>>
document.getElementById('AI_SUMMARY').innerHTML = "<b>Answer:</b> The capital of India is New Delhi.";
<<<END>>>

EXAMPLE 2 (Chart Request):
<<<TARGET>>>
canvas_1
<<<DESCRIPTION>>>
Sales Bar Chart
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

        // --- CUSTOM PARSER (Looping Regex) ---
        const regex = /<<<TARGET>>>\s*(\S+)\s*<<<DESCRIPTION>>>\s*([\s\S]*?)\s*<<<JAVASCRIPT>>>\s*([\s\S]*?)\s*<<<END>>>/gi;
        let match;
        let foundAny = false;

        while ((match = regex.exec(reply)) !== null) {
            foundAny = true;
            const targetId = match[1].trim();
            const description = match[2].trim();
            let code = match[3].trim();

            // --- AUTO-CORRECT CAPS LOCK ---
            code = code
                .replace(/DOCUMENT\.QUERYSELECTOR/gi, "document.querySelector")
                .replace(/DOCUMENT\.GETELEMENTBYID/gi, "document.getElementById")
                .replace(/APP\.DATA/gi, "APP.data")
                .replace(/APP\.CHARTS/gi, "APP.charts")
                .replace(/NEW APEXCHARTS/gi, "new ApexCharts");

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
