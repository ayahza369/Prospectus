import { Spectrum } from "spectrum-ts";
import { imessage } from "spectrum-ts/providers/imessage";
import { terminal } from "spectrum-ts/providers/terminal";

const app = await Spectrum({
  projectId: process.env.PROJECT_ID!,
  projectSecret: process.env.PROJECT_SECRET!,
  providers: [
    imessage.config(),
    terminal.config(),
  ]
});

for await (const [space, message] of app.messages) {
  await space.responding(async () => {
    await message.reply("Hello from Spectrum.");
  });
}