
// --- SYSTEM PROMPT BUILDER (Balanced Version) ---
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

EXAMPLE:
<<<TARGET>>>
canvas_1
<<<DESCRIPTION>>>
Sales Bar Chart
<<<JAVASCRIPT>>>
APP.charts.c1?.destroy();
var opt = { series: [{ data: [10, 20] }], chart: { type: 'bar' } };
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

        // --- CUSTOM PARSER (Regex) ---
        // Captures Target, Description, and Javascript reliably
        const regex = /<<<TARGET>>>\s*(\S+)\s*<<<DESCRIPTION>>>\s*([\s\S]*?)\s*<<<JAVASCRIPT>>>\s*([\s\S]*?)\s*<<<END>>>/i;
        const match = reply.match(regex);

        if (!match) {
            throw new Error("Invalid AI response format. Could not parse custom delimiters.");
        }

        const targetId = match[1].trim();
        const description = match[2].trim();
        const code = match[3].trim();

        addMsg("ai", `<strong>${targetId}:</strong> ${description}`);

        // --- EXECUTION (No if/else, pure dynamic execution) ---
        // We pass APP, document, ApexCharts to the function scope
        const fn = new Function("APP", "document", "ApexCharts", code);
        fn(APP, document, ApexCharts);

        addLog("✅ Executed on " + targetId, "success");

    } catch (e) {
        addLog("❌ ERROR: " + e.message, "error");
        addMsg("system", "Error: " + e.message);
    } finally {
        setChatState("ready");
    }
}
