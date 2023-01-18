# IronHeartBot

---------------

This is a code for the iron heart bot. Iron heart bot has gpt and dalle command.

## Install and Setup

### Git

If you have git installed, you can run this command

```cmd
git clone https://github.com/najis-poop/IronHeartBot .
```

Note that this would put all the files in the current directory you are in so make sure you run the command
in empty directory.

### Manually

If you don't have git installed, you can download this repo manually and unzip it to the directory.

### Setup

After you done installing it, you will see that there is file named `.env`
You can put your discord bot and openai token there.

```env
OPENAI_TOKEN=your openai token here
BOT_TOKEN=your bot token here
TEST_TOKEN=you don't need this usually. just remove it
```

Now you need to create db folder for the database. IronHeart use TinyDB (a simple database that use json format)
so you don't need to setup a sql or anything.

_Note: If you get an error like file not found, try create `template_prompt.db` and `tag.db` inside `db` directory._

You now can run the bot.

## LICENSE

The MIT License (MIT)
