local ADDON_CONFIG_PATH = "../addons/skillchat/config.json"
local acutil = require("acutil")

local defaultChatSystem = CHAT_SYSTEM
local defaultToLuaCast = tolua.cast
local defaultSessionGetSkill = session.GetSkill
local defaultSessionGetSkillOverheat = session.GetSklOverHeat
local defaultGetIES = GetIES

local defaultUIChat = nil
local defaultIconUse = nil
local defaultIconOnCooltimeEnd = nil
local defaultIconUpdateSkillCooldown = nil

local loaded = false
local config={}
local states={}

local function loadConfig()
  local loadedConfig, error = acutil.loadJSON(ADDON_CONFIG_PATH)
  if error then
    defaultChatSystem("skillchat: error loading config.")
    return
  end
  for skillClassName, skillConfig in pairs(loadedConfig) do
    if type(skillConfig) == "table" then
      for key, text in pairs(skillConfig) do
        if type(text) ~= "string" then
          defaultChatSystem("skillchat: unable to load config; " .. skillClassName .. "." .. key .. " is not a string.")
          return
        end
        if IsBadString(text) ~= nil then
          defaultChatSystem("skillchat: unable to load config; bad string found at " .. skillClassName .. "." .. key .. ".")
          return
        end
      end
    end
  end
  for skillClassName, skillConfig in pairs(loadedConfig) do
    if type(skillConfig) == "table" then
      if not states[skillClassName] then
        states[skillClassName] = {ready=true, overheatTime=0, cooldownTimeSeconds=0}
      end
    end
  end
  config = loadedConfig
  loaded = true
  defaultChatSystem("skillchat: config loaded.")
end

local function enableSkillChat()
  config.enabled = true
  defaultChatSystem("skillchat: enabled.")
  local _, error = acutil.saveJSON(ADDON_CONFIG_PATH, config)
  if error then
    defaultChatSystem("skillchat: error saving config.")
  end
end

local function disableSkillChat()
  config.enabled = false
  defaultChatSystem("skillchat: disabled.")
  local _, error = acutil.saveJSON(ADDON_CONFIG_PATH, config)
  if error then
    defaultChatSystem("skillchat: error saving config.")
  end
end

local function parseChatCommand(arguments)
  local command = arguments[1]
  if command then
    if command == "load" then
      loadConfig()
    elseif command == "on" then
      enableSkillChat()
    elseif command == "off" then
      disableSkillChat()
    else
      defaultChatSystem("skillchat: invalid command.")
    end
  else
    defaultChatSystem("skillchat: invalid usage; no command provided.")
  end
end

local function extractIconData(icon)
  local iconInfo = defaultToLuaCast(icon, "ui::CIcon"):GetInfo()
  if iconInfo:GetCategory() == "Skill" then
    local skillInfo = defaultSessionGetSkill(iconInfo.type)
    if skillInfo then
      local skillObject = defaultGetIES(skillInfo:GetObject())
      local skillConfig = config[skillObject.ClassName] or nil
      local skillState = states[skillObject.ClassName] or nil
      if skillObject then
        return iconInfo, skillInfo, skillObject, skillConfig, skillState
      end
    end
  end
end

local function iconUse(icon, reAction)
  if config.enabled ~= false then
    local _, _, skillObject, skillConfig, skillState = extractIconData(icon)
    if skillConfig and skillState then
      if skillConfig.onPress and skillState.ready then
        defaultUIChat(skillConfig.onPress:gsub("%%s", skillObject.Name))
      end
    end

    if config.debug then
      defaultChatSystem("skillchat: " .. skillObject.ClassName)
    end
  end
  return defaultIconUse(icon, reAction)
end

local function iconOnCooltimeEnd(frame, icon, argStr, argNum)
  local _, _, skillObject, skillConfig, skillState = extractIconData(icon)
  if skillConfig and skillState then
    if config.enabled ~= false and skillConfig.onReady then
      defaultUIChat(skillConfig.onReady:gsub("%%s", skillObject.Name))
    end
    skillState.ready = true
    skillState.overheatTime = 0
    skillState.cooldownTimeSeconds = 0
  end
  return defaultIconOnCooltimeEnd(frame, icon, argStr, argNum)
end

--[[
behavior notes:
overheat (skillObject.OverHeatGroup == "None" or overheatTime == 0)
  overheatResetTime = session.GetSklOverHeatResetTime(iconInfo.type)
  overheatTime = session.GetSklOverHeat(iconInfo.type) : multiple of overheatResetTime (0 = ready/on cooldown, number of spent overheats = ceil(overheatTime/overheatResetTime) - 1).
  on final cast the skill goes into cd and uses normal cd mechanics.
normal cd
  totalTime = skillInfo:GetTotalCoolDownTime()
  currentTime = skillInfo:GetCurrentCoolDownTime()
  totalTime is fixed cooldown time listed on the skill.
  currentTime starts at totalTime (= on cd) and counts down to zero (= ready).
--]]
local function iconUpdateSkillCooldown(icon)
  local iconInfo, skillInfo, skillObject, skillConfig, skillState = extractIconData(icon)
  if skillConfig and skillState then
    local currentTime = skillInfo:GetCurrentCoolDownTime() or 0
    local overheatTime = defaultSessionGetSkillOverheat(iconInfo.type) or 0
    -- ready -> went on cooldown
    if skillState.ready and currentTime > 0 then
      if config.enabled ~= false and skillConfig.onCast then
        defaultUIChat(skillConfig.onCast:gsub("%%s", skillObject.Name))
      end
      skillState.ready = false
    -- ready -> overheat spent
    elseif skillState.ready and overheatTime > skillState.overheatTime then
      if config.enabled ~= false and skillConfig.onCast then
        defaultUIChat(skillConfig.onCast:gsub("%%s", skillObject.Name))
      end
      skillState.overheatTime = overheatTime
    end

    -- track cooldown
    if config.enabled ~= false then
      local currentTimeSeconds = math.ceil(currentTime/1000)
      local key = "onCooldown" .. currentTimeSeconds
      if currentTime > 0 and skillConfig[key] and skillState.cooldownTimeSeconds ~= currentTimeSeconds then
        skillState.cooldownTimeSeconds = currentTimeSeconds
        defaultUIChat(skillConfig[key]:gsub("%%s", skillObject.Name):gsub("%%t", currentTimeSeconds))
      end
    end

    -- silent reconcile for other state transitions
    -- force ready state
    if currentTime == 0 and overheatTime == 0 then
      skillState.ready = true
      skillState.overheatTime = 0
      skillState.cooldownTimeSeconds = 0
    -- force overheat state
    elseif not skillState.ready and overheatTime > 0 then
      skillState.ready = true
      skillState.overheatTime = overheatTime
      skillState.cooldownTimeSeconds = 0
    end
  end
  return defaultIconUpdateSkillCooldown(icon)
end

function SKILLCHAT_ON_INIT()
  acutil.slashCommand("skillchat", parseChatCommand)
  if not defaultUIChat then
    defaultUIChat = ui.Chat
  end
  if not defaultIconUse then
    defaultIconUse = ICON_USE
    ICON_USE = iconUse
  end
  if not defaultIconOnCooltimeEnd then
    defaultIconOnCooltimeEnd = ICON_ON_COOLTIMEEND
    ICON_ON_COOLTIMEEND = iconOnCooltimeEnd
  end
  if not defaultIconUpdateSkillCooldown then
    defaultIconUpdateSkillCooldown = ICON_UPDATE_SKILL_COOLDOWN
    ICON_UPDATE_SKILL_COOLDOWN = iconUpdateSkillCooldown
  end
  if not loaded then
    loadConfig()
  end
end
