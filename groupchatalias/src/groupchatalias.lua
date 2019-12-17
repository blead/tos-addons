local ADDON_CONFIG_PATH = "../addons/groupchatalias/aliases.json"
local CHAT_TYPE_COMMANDS = {["/s"]=true, ["/y"]=true, ["/p"]=true, ["/g"]=true, ["/w"]=true, ["/r"]=true}
local COMMAND_PORTION_START = 0
local COMMAND_PORTION_GCHAT = 1
local COMMAND_PORTION_COMMAND = 2
local COMMAND_PORTION_F = 3
local COMMAND_PORTION_END = 4
local acutil = require("acutil")

local next = next
local defaultChatSystem = CHAT_SYSTEM
local defaultGetChatFrame = GET_CHATFRAME
local defaultGetChild = GET_CHILD
local defaultUIChat = nil
local defaultUILeaveGroupOrWhisperChat = nil

local ready = false
local aliases = {}
local groups = {}

local function removeAlias(alias)
  if not aliases[alias] then
    defaultChatSystem("groupchatalias: alias '" .. alias .. "' does not exist.")
    return
  end
  groups[aliases[alias]] = nil
  aliases[alias] = nil
  defaultChatSystem("groupchatalias: alias '" .. alias .. "' removed.")
  local _, error = acutil.saveJSON(ADDON_CONFIG_PATH, aliases)
  if error then
    defaultChatSystem("groupchatalias: error saving config.")
  end
end

local function createAlias(alias, groupid)
  if aliases[alias] then
    defaultChatSystem("groupchatalias: alias '" .. alias .. "' already exists.")
    return
  end
  if groups[groupid] then
    removeAlias(groups[groupid])
  end
  aliases[alias] = groupid
  groups[groupid] = alias
  defaultChatSystem("groupchatalias: alias '" .. alias .. "' created.")
  local _, error = acutil.saveJSON(ADDON_CONFIG_PATH, aliases)
  if error then
    defaultChatSystem("groupchatalias: error saving config.")
  end
end

local function removeGroup(groupid)
  local alias = groups[groupid]
  if not alias then
    defaultChatSystem("groupchatalias: no alias created.")
    return
  end
  aliases[alias] = nil
  groups[groupid] = nil
  defaultChatSystem("groupchatalias: alias '" .. alias .. "' removed.")
  local _, error = acutil.saveJSON(ADDON_CONFIG_PATH, aliases)
  if error then
    defaultChatSystem("groupchatalias: error saving config.")
  end
end

local function resetAliases()
  aliases = {}
  groups = {}
  defaultChatSystem("groupchatalias: removing all aliases.")
  local _, error = acutil.saveJSON(ADDON_CONFIG_PATH, aliases)
  if error then
    defaultChatSystem("groupchatalias: error saving config.")
  end
end

local function listAliases()
  local list = {}
  local i = 1
  for alias, _ in pairs(aliases) do
      list[i] = alias
      i = i + 1
  end
  return list
end

local function escapePattern(text)
  return text:gsub("([^%w])", "%%%1")
end

local function uiChat(text)
  -- group chat
  local groupid, rest = text:match("^/f (%d+) /gchat(.*)")
  if groupid then
    local command, alias = rest:match("^ (%S+) ?(%S*)")
    if not command then
      defaultChatSystem("groupchatalias: invalid usage; no command provided.")
    elseif command == "alias" then
      if alias ~= "" then
        createAlias(alias, groupid)
      else
        defaultChatSystem("groupchatalias: invalid usage; no alias provided.")
      end
    elseif command == "remove" then
      removeGroup(groupid)
    elseif command == "show" then
      local groupAlias = groups[groupid]
      if groupAlias then
        defaultChatSystem("groupchatalias: " .. groupAlias .. ".")
      else
        defaultChatSystem("groupchatalias: no alias created.")
      end
    elseif command == "reset" then
      resetAliases()
    else
      defaultChatSystem("groupchatalias: invalid command.")
    end
    return defaultUIChat("/f " .. groupid)
  end

  -- other channels
  local commandPortion = COMMAND_PORTION_START
  local isCommand = false
  for word in text:gmatch("%S+") do
    if not CHAT_TYPE_COMMANDS[word] then
      if commandPortion == COMMAND_PORTION_START and word == "/gchat" then
        commandPortion = COMMAND_PORTION_GCHAT
        isCommand = true
      elseif commandPortion == COMMAND_PORTION_START and word == "/f" then
        commandPortion = COMMAND_PORTION_F
        isCommand = true
      elseif commandPortion == COMMAND_PORTION_GCHAT then
        if word == "alias" then
          commandPortion = COMMAND_PORTION_END
          defaultChatSystem("groupchatalias: invalid usage; use '/gchat " .. word .. "' in a group chat.")
          break
        elseif word == "remove" then
          commandPortion = COMMAND_PORTION_COMMAND
        elseif word == "reset" then
          commandPortion = COMMAND_PORTION_END
          resetAliases()
          break
        elseif word == "show" then
          commandPortion = COMMAND_PORTION_END
          if next(aliases) == nil then
            defaultChatSystem("groupchatalias: no alias found.")
          else
            defaultChatSystem("groupchatalias: list of all aliases:{nl}" .. table.concat(listAliases(), "{nl}"))
          end
          break
        else
          commandPortion = COMMAND_PORTION_END
          defaultChatSystem("groupchatalias: invalid command.")
          break
        end
      elseif commandPortion == COMMAND_PORTION_COMMAND then
        commandPortion = COMMAND_PORTION_END
        removeAlias(word)
        break
      elseif commandPortion == COMMAND_PORTION_F then
        if aliases[word] then
          return defaultUIChat(text:gsub("/f%s+" .. escapePattern(word), "/f " .. aliases[word]))
        elseif groups[word] then
          isCommand = false
          break
        else
          commandPortion = COMMAND_PORTION_END
          defaultChatSystem("groupchatalias: alias '" .. word .. "' not found.")
          break
        end
      else
        break
      end
    end
  end

  if not isCommand then
    return defaultUIChat(text)
  end

  -- /gchat
  if commandPortion == COMMAND_PORTION_GCHAT then
    defaultChatSystem("groupchatalias: invalid usage; no command provided.")
  -- /gchat remove
  elseif commandPortion == COMMAND_PORTION_COMMAND or commandPortion == COMMAND_PORTION_F then
    defaultChatSystem("groupchatalias: invalid usage; no alias provided.")
  end
  return defaultUIChat("")
end

local function uiLeaveGroup(groupid)
  if groups[groupid] then
    removeGroup(groupid)
  end
  return defaultUILeaveGroupOrWhisperChat(groupid)
end

function GROUPCHATALIAS_ON_TYPE(_, ctrl)
  local text = ctrl:GetText()
  local alias = text:match("^/f (%S+)")
  if alias and aliases[alias] then
    ctrl:SetText("/f " .. aliases[alias])
  end
end

function GROUPCHATALIAS_ON_INIT()
  if not defaultUIChat then
    defaultUIChat = ui.Chat
    ui.Chat = uiChat
  end
  if not defaultUILeaveGroupOrWhisperChat then
    defaultUILeaveGroupOrWhisperChat = ui.LeaveGroupOrWhisperChat
    ui.LeaveGroupOrWhisperChat = uiLeaveGroup
  end
  if not ready then
    aliases = acutil.loadJSON(ADDON_CONFIG_PATH, nil, true)
    for alias, groupid in pairs(aliases) do
      groups[groupid] = alias
    end
    ready = true
  end
  local mainchatEditControl = defaultGetChild(defaultGetChatFrame(), "mainchat", "ui::CEditControl")
  if not mainchatEditControl then
    defaultChatSystem("groupchatalias: failed to get chat frame")
    return
  end
  mainchatEditControl:SetTypingScp("GROUPCHATALIAS_ON_TYPE")
end
