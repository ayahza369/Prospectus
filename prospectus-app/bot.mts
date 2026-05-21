import { Spectrum } from "spectrum-ts";
import { imessage } from "spectrum-ts/providers/imessage";
import { terminal } from "spectrum-ts/providers/terminal";

const FINWHISPER_URL = process.env.FINWHISPER_URL ?? "http://localhost:8000/query";

const app = await Spectrum({
  projectId: process.env.PROJECT_ID!,
  projectSecret: process.env.PROJECT_SECRET!,
  providers: [
    imessage.config(),
    // terminal.config(),
  ]
});

async function askFinWhisper(text: string): Promise<string> {
  const res = await fetch(FINWHISPER_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: { text } }),
  });
  if (!res.ok) return "FinWhisper is unavailable right now. Try again in a moment.";
  const data = await res.json() as { reply?: string };
  return data.reply ?? "No response from FinWhisper.";
}

for await (const [space, message] of app.messages) {
  await space.responding(async () => {
    const reply = await askFinWhisper(message.text);
    await space.send(reply);
  });
}
