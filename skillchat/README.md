# skillchat
Send chat messages based on skill cooldowns.

## Description
This addon is inspired by [cdtracker](https://github.com/NoctisCepheus/ToS-Addons-Cepheus/tree/master/cdtracker-rebuild). It is a more lightweight alternative I made to solve some issues I have with cdtracker.  
It is specifically made just for sending chat messages based on skill cooldowns, and does not include any other alerting functions as opposed to cdtracker.

## Installation
Install via [Addon Manager](https://github.com/JTosAddon/Tree-of-Savior-Addon-Manager#tree-of-savior-addon-manager).

## Manual Installation
**Note: This requires [acutil](https://github.com/Tree-of-Savior-Addon-Community/AC-Util/) which comes with addon manager by default.**

Normally, the addon manager will do this for you:

1. Put the addon file in `TreeOfSavior/data` directory. Make sure that the file name includes a unicode character (you can name the file `_skillchat-🍞-v0.2.0.ipf` for example) so it does not get removed by the game.
2. Create a new directory `TreeOfSavior/addons/skillchat`.

## Configuration

A configuration file is required for the addon to work. Create a plain text configuration file in `TreeOfSavior/addons/skillchat`. Name it `config.json`.  
The configuration file is in strict JSON format. Here is an example with 2 skills tracked:

```json
{
  "Cleric_Heal": {
    "onPress": "/p Casting %s.",
    "onCast": "/p %s cast!"
  },
  "Cleric_Cure": {
    "onPress": "/p Casting %s.",
    "onCast": "/p %s cast!",
    "onReady": "/p %s ready!",
    "onCooldown3": "/p %s ready in %t seconds.",
    "onCooldown5": "/p %s ready in %t seconds."
  }
}
```

- Top level keys are `ClassName`s of skills. This can be found on sites like https://tos.neet.tv/, or from using [debug mode](#debug-mode).
- There are multiple events available which can trigger sending a chat message. All events are optional. You can simply remove them if you do not want to utilize them.
  - `onPress`: This is like cdtracker's message on cast functionality. It is triggered when you press the skill button. Note that it will trigger even if the skill was not cast (e.g., when you are in an animation delay or lagging).
  - `onCast`: This is a bit more specialized version of `onPress`, it tracks the usage of skills through cooldowns (or overheats if applicable) and will trigger just after the skill has been cast.
  - `onReady`: This will trigger when the skill is ready.
  - `onCooldownX` where X is an integer: This will trigger when the cooldown reaches X seconds.
- The messages are simply the same as the ones you can normally send in chat. Adding `/p` will send it to party chat, for example. There are some extra parameters you can use which will be dynamically replaced by the addon:
  - `%s`: skill name.
  - `%t`: remaining cooldown in seconds. Only usable in `onCooldownX` events.

## Debug mode
Generally `ClassName` of a skill is in the format of `Class_Skill` (e.g., `Cleric_Heal`). For set effects, it is `EquipmentSet_Skill` (e.g., `Velcoffer_Sumazinti`).
If you do not know what the `ClassName` of the skill you want is, debug mode is one way to find out.

To enable debug mode, put `"debug": true` in the top level of your configuration as shown below:

```json
{
  "debug": true,
  "Cleric_Heal": {
    "onPress": "/p Casting %s.",
    "onCast": "/p %s cast!"
  },
  "Cleric_Cure": {
    "onPress": "/p Casting %s.",
    "onCast": "/p %s cast!",
    "onReady": "/p %s ready!",
    "onCooldown3": "/p %s ready in %t seconds.",
    "onCooldown5": "/p %s ready in %t seconds."
  }
}
```

Then, every time you press a skill (`onPress` event), the addon will also output the `ClassName` of the skill in system chat.

## Enabled Flag
There's an optional top-level `enabled` flag which will be written automatically by the addon if you ever toggle it. The default value is `true`.

```json
{
  "enabled": true,
  "debug": true,
  "Cleric_Heal": {
    "onPress": "/p Casting %s.",
    "onCast": "/p %s cast!"
  },
  "Cleric_Cure": {
    "onPress": "/p Casting %s.",
    "onCast": "/p %s cast!",
    "onReady": "/p %s ready!",
    "onCooldown3": "/p %s ready in %t seconds.",
    "onCooldown5": "/p %s ready in %t seconds."
  }
}
```

It does what it says: when `enabled` is `true`, messages will be sent to chat, otherwise nothing will be sent.
Setting this to `false` also disables debug mode.

## Commands

### `/skillchat load`
(Re)loads the configuration from `TreeOfSavior/addons/skillchat/config.json`.
Type it in chat to reload the configuration so that you do not need to restart the game when making changes.

### `/skillchat on`
Set `enabled` to `true`, enabling all messages.

### `/skillchat off`
Set `enabled` to `false`, disabling all messages.

## FAQs

### The addon cannot find my configuration file!
Make sure the file is really named `config.json` and not `config.json.txt` or any other common extensions.  
Try making Windows show file name extensions to be sure.

## Changelog
- v0.2.0
  - Implement `enabled` flag.
- v0.1.0
  - Initial implementation.
