# Set up a morning brief that runs while you sleep

A guide for MRKT 3533 students, written October 21, 2026. It walks
through what we did on stage: a brief that reads your calendar and
your email every weekday morning and tells you what matters today.
Twenty minutes to set up, in Claude or in ChatGPT. The order matters.
Privacy settings come first, then a look at what you are about to
share, then the connection, then the task.

## Step 1. Turn off training on your data

Do this before you connect anything. Both apps default to using your
chats to improve their models. Once a calendar or an inbox is feeding
those chats, that default covers more than you think.

Claude: open Settings, then Privacy, and turn off "Help improve
Claude." The page is at https://claude.ai/settings/privacy. Anthropic
says it does not train on what the Gmail and Calendar connectors
retrieve. But anything you paste from them, or that shows up in a
response, falls under this toggle while it is on. Turning it off also
drops chat retention from up to five years to thirty days.

ChatGPT: open your account menu, then Settings, then Data controls.
Turn off "Improve the model for everyone." On the phone app it is
under your profile icon, then Settings, then Data controls. OpenAI
says it does not train on data pulled directly from connected Google
apps. But once that data appears in a response, or you paste it in,
it can be used for training unless this setting is off. While you are there, look
at Settings, then Personalization: with Memory on, ChatGPT may keep
details it learned from your inbox.

## Step 2. Decide what it gets to see

The permission screen is the real scope, and the prompt is a polite
request. When you connect Gmail, Google asks you to grant access to
the whole mailbox, not the last two weeks. In both apps the grant
includes the ability to send or change mail. When you connect
Calendar, the grant covers every calendar you can see, including
shared ones, with attendee names and meeting links.

Before you click Allow, scan your inbox and calendar for five things:

- Other people's information: a group project thread, a roommate's
  lease, a parent's medical update.
- Anything from a job: an employer's customer list, a manager's
  forwarded spreadsheet, an internship offer with a salary in it.
- Money: bank alerts, Venmo and Zelle receipts, tuition statements.
- Health and identity: appointment reminders, insurance, anything with
  a Social Security number or a passport in it.
- Passwords and codes: password reset emails, two-factor codes,
  account recovery links.

If one of those is in there, you have three choices. Leave it and
accept that an agent will read it. Clean it out first, which is a
good afternoon's work anyway. Or make a separate Google account for
the brief, forward only the calendar and the mail you want read, and
connect that. The third option is what I'd pick if a job inbox is
involved.

Two more habits. Disconnect the app when the semester ends, in Claude
at https://claude.ai/customize/connectors and in ChatGPT under
Settings, then Apps. And know that disconnecting does not delete what
the app already saved in past chats or memories. Delete those
separately if it matters.

## Step 3. Connect Google Calendar and Gmail

Claude: open https://claude.ai/customize/connectors, find Google
Calendar and Gmail, and connect each with the Google account you
chose in Step 2. Google's screen will mention sending email. Claude
asks before each send in a normal chat. In a scheduled task set to
run without asking, it won't, so keep the task's instructions to
reading only, which the template already does.

ChatGPT: open Settings, then Apps, and connect Gmail and Google
Calendar. ChatGPT asks Google for permission to read and modify mail
and to read and edit calendar events, so the same caution applies.

## Step 4. Create the brief

Claude, on a Pro plan or above: open Scheduled in the left sidebar,
then Templates, then Daily briefing. Claude writes the task for you
and sets it to weekdays at 8:00. Open the task, click the schedule,
change the time to the one you want, and save. Press Run now to see
the first one. A run takes about four minutes. The result is a
one-page brief, and you get a notification when it is ready.

ChatGPT, on any plan: open Scheduled and type the sentence we used on
stage:

> Set up a scheduled task that gives me a morning brief each weekday
> at 7am: what's on my calendar, important unread emails or messages,
> and anything that needs my attention today. Keep it short and
> scannable.

On the free plan the brief arrives "in the morning" rather than at
7:00. You can have three tasks at a time. Exact times need the Go
plan.

## Step 5. Iterate with it

The first brief will be wrong somewhere. It will rank a Handshake
blast above a professor, or tell you to start studying on Monday for
Thursday's quiz. That is the point of the first week. Open the run,
tell it what it got wrong in one sentence, and the next morning's
brief gets closer. After three or four mornings, edit the task's
instructions with what you learned about who counts as a real person,
what to skip, and how far ahead to look.

A brief is working when you read it on your phone before you get out
of bed and nothing in it surprises you by noon.

## What it costs

| App | Lowest plan with a scheduled brief | Exact-time delivery | Monthly price |
| --- | --- | --- | --- |
| Claude | Pro | Yes | $20 |
| ChatGPT | Free | No, a morning window | $0 |
| ChatGPT | Go | Yes | $8 |

Prices are United States list prices as of October 2026.

## Sources

- Anthropic, Schedule recurring tasks in Claude Cowork:
  https://support.claude.com/en/articles/13854387-schedule-recurring-tasks-in-claude-cowork
- Anthropic, Use Google Workspace connectors:
  https://support.claude.com/en/articles/10166901-use-google-workspace-connectors
- OpenAI, Data controls in ChatGPT:
  https://help.openai.com/en/articles/7730893-data-controls-in-chatgpt
- OpenAI, Google app data controls FAQ:
  https://help.openai.com/en/articles/10408842-google-app-data-controls-faq
- OpenAI, Scheduled tasks in ChatGPT:
  https://help.openai.com/en/articles/10291617-scheduled-tasks-in-chatgpt
