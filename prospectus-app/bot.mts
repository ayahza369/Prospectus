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

const im = imessage(app);
const user = await im.user(process.env.USER_PHONE_NUMBER!);
const dm = await im.space(user);
await dm.send("Hello user! This is a message from Spectrum.");

/*
for await (const [space, message] of app.messages) {
  await space.responding(async () => {
    await message.reply("Hello from Spectrum.");
  });
}
*/