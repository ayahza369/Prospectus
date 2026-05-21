import { Spectrum } from "spectrum-ts";
import { imessage } from "spectrum-ts/providers/imessage";
import { terminal } from "spectrum-ts/providers/terminal";

const FINWHISPER_URL = process.env.FINWHISPER_URL ?? "http://127.0.0.1:8000/query";

const app = await Spectrum({
  projectId: process.env.PROJECT_ID!,
  projectSecret: process.env.PROJECT_SECRET!,
  providers: [
    imessage.config(),
    // terminal.config(),
  ]
});

async function askFinWhisper(text: string): Promise<string> {
  try {
    const res = await fetch(FINWHISPER_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: { text } }),
    });
    if (!res.ok) {
      const errText = await res.text();
      return `FinWhisper is unavailable right now. Status: ${res.status}. Body: ${errText}`;
    }
    const data = await res.json() as { reply?: string };
    return data.reply ?? "No response from FinWhisper.";
  } catch (error) {
    console.error("Fetch to FinWhisper failed:", error);
    return `Error connecting to FinWhisper: ${error instanceof Error ? error.message : String(error)}`;
  }
}

for await (const [space, message] of app.messages) {
  await space.responding(async () => {
    const reply = await askFinWhisper(message.content.text);
    await space.send(reply);
  });
}
