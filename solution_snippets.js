
// --- SYSTEM PROMPT BUILDER (Strict Version) ---
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

3. BEHAVIOR:
- If user says "hi" or general chat: Target AI_SUMMARY only.
- DO NOT generate charts unless explicitly asked.

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

    // IMPORTANT: We do NOT send chat history.
    // We strictly send the System Prompt + Current Request to keep the context clean.
    const prompt = buildSystemPrompt(req);

    try {
        setChatState("disabled");
        addMsg("system", "Thinking...");

        // Call AI with a single message (User role containing the full system instruction)
        const res = await callAI([{ role: "user", content: prompt }]);
        const reply = res.choices[0].message.content.trim();

        addLog("ai-code", reply);

        // --- CUSTOM PARSER (Looping Regex) ---
        // Captures ALL targets in the response
        const regex = /<<<TARGET>>>\s*(\S+)\s*<<<DESCRIPTION>>>\s*([\s\S]*?)\s*<<<JAVASCRIPT>>>\s*([\s\S]*?)\s*<<<END>>>/gi;
        let match;
        let foundAny = false;

        while ((match = regex.exec(reply)) !== null) {
            foundAny = true;
            const targetId = match[1].trim();
            const description = match[2].trim();
            const code = match[3].trim();

            addMsg("ai", `<strong>${targetId}:</strong> ${description}`);

            // --- EXECUTION ---
            try {
                const fn = new Function("APP", "document", "ApexCharts", code);
                fn(APP, document, ApexCharts);
                addLog("✅ Executed on " + targetId, "success");
            } catch (err) {
                addLog("❌ Exec Error (" + targetId + "): " + err.message, "error");
            }
        }

        if (!foundAny) {
            // Fallback if regex fails but there is text (maybe simple chat?)
             addLog("⚠️ No code block found. AI said: " + reply, "warn");
             addMsg("ai", reply);
        }

    } catch (e) {
        addLog("❌ ERROR: " + e.message, "error");
        addMsg("system", "Error: " + e.message);
    } finally {
        setChatState("ready");
    }
}
