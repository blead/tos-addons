# groupchatalias
Create group chat aliases for easier switching commands.

## Description
Normally we can type `/f <groupid>`, where `<groupid>` is a 15-digit number identifying the group chat we want, to switch or send messages to that specific group chat channel.  
However, this identifier is hard to remember and super impractical for regular usage. This addon aims to solve that by providing a way to create aliases for group chat.  

## Installation
Install via [Addon Manager](https://github.com/JTosAddon/Tree-of-Savior-Addon-Manager#tree-of-savior-addon-manager).

## Manual Installation
**Note: This requires [acutil](https://github.com/Tree-of-Savior-Addon-Community/AC-Util/) which comes with addon manager by default.**

Normally, the addon manager will do this for you:

1. Put the addon file in `TreeOfSavior/data` directory. Make sure that the file name includes a unicode character (you can name the file `_groupchatalias-🍞-v0.1.0.ipf` for example) so it does not get removed by the game.
2. Create a new directory `TreeOfSavior/addons/groupchatalias`.

## Quick Start
1. Type `/gchat alias <alias>` (replace `<alias>` with any name you want, note that it cannot contain spaces) in a group chat to create an alias for that channel.
2. To use the created alias, simply type `/f <alias>` and the addon will do the work for you. This works both in chat and macros.
    - If typed directly in chat, the alias will be instantly replaced by the group id.
    - If used in macros, the addon will process the message and replace the alias with the group id accordingly.

## Group Chat Commands
The following commands are available only in a group chat. Similar commands may exist but behave differently when used outside of a group chat.

### `/gchat alias <alias>`
Create an alias named `<alias>` for the group chat.

### `/gchat remove`
Remove the alias of the group chat.

### `/gchat show`
Show the registered alias of the group chat.

## Non-group Chat Commands
The following commands are available only outside of a group chat (any regular channels). Similar commands may exist but behave differently when used inside a group chat.

### `/gchat remove <alias>`
Remove the alias named `<alias>`.

### `/gchat show`
Show all aliases currently registered.

## Global Commands
The following commands work the same everywhere.

### `/gchat reset`
Remove all aliases ever created.

## Changelog
- v0.1.0
  - Initial implementation.
