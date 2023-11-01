# LG HUB WEBSOCKET ENDPOINTS

```
/assignment
/assignment/list
/assignment/list/effective

/audio/%s/audio_player_state
/audio/%s/automatic_noise_reduction
/audio/%s/bass_level
/audio/%s/blue_voice
/audio/%s/blue_voice_2
/audio/%s/blue_voice_2/effects
/audio/%s/blue_voice_2/enabled
/audio/%s/blue_voice_2/meter/data
/audio/%s/blue_voice_2/meter/watch
/audio/%s/blue_voice_2/record_playback
/audio/%s/blue_voice_2/sample/action
/audio/%s/blue_voice/enabled
/audio/%s/blue_voice/meter/data
/audio/%s/blue_voice/meter/watch
/audio/%s/blue_voice/record_playback
/audio/%s/centurion_mix
/audio/%s/centurion_mix_info
/audio/%s/centurion/0601_micmute
/audio/%s/centurion/0604_sidetone
/audio/%s/centurion/equalizer
/audio/%s/centurion/mic_mute
/audio/%s/centurion/mixer_mic
/audio/%s/centurion/mixer_mic/information
/audio/%s/centurion/mute
/audio/%s/centurion/onboard_equalizer
/audio/%s/centurion/onboard_equalizer/save
/audio/%s/centurion/onboard_noise_reduction
/audio/%s/centurion/volume
/audio/%s/effects
/audio/%s/equalizer
/audio/%s/equalizer_manager/configuration
/audio/%s/equalizer_manager/default_card
/audio/%s/equalizer_manager/information
/audio/%s/file/start
/audio/%s/file/stop
/audio/%s/fix_hypersonic_mic_defaults
/audio/%s/hardware_noise_reduction
/audio/%s/headset_tones
/audio/%s/lightspeed_connection
/audio/%s/mic_mute_toggle
/audio/%s/mixing_matrix
/audio/%s/mixing_matrix/info
/audio/%s/mixing_matrix/state
/audio/%s/molding_prep_mode
/audio/%s/mute
/audio/%s/mute_notification
/audio/%s/onboard
/audio/%s/platform_id
/audio/%s/pro_equalizer
/audio/%s/pro_equalizer_eeprom
/audio/%s/sample/action
/audio/%s/sidetone
/audio/%s/start_surround_sound_test
/audio/%s/stop_surround_sound_test
/audio/%s/surround_sound
/audio/%s/tap_action_list
/audio/%s/tap_user_action
/audio/%s/volume
/audio/%s/volume_notifications
/audio/blue_voice_2/sample/card_validation
/audio/equalizer_cycle/notification
/audio/surround_sound/notification

/axis_mapping/%s/report_axis_changed
/axis_monitor/%s/list
/axis_monitor/%s/monitor
/axis_monitor/%s/packed_monitor
/axis_monitor/event

/battery/%s/check
/battery/%s/power_consumption/changed
/battery/%s/sleep_timer
/battery/%s/state
/battery/%s/state/changed
/battery/%s/warning
/battery/state/changed
/battery/warning

/center_spring/%s/change
/center_spring/%s/value
/centurion/%s/start_pairing
/centurion/%s/stop_pairing

/charge_pad/%s/charge_control
/charge_pad/%s/paired_device
/charge_pad/%s/pairing_disconnect
/charge_pad/charging/enable
/charge_pad/osd/paired_device/battery/low

/configuration_profile/%s/active_profile
/configuration_profile/%s/active_profile/changed
/configuration_profile/%s/info
/configuration_profile/%s/is_ghub_profile_active
/configuration_profile/%s/profile_name
/configuration_profile/%s/profile_names

/devices/%s/blocker/resolve
/devices/%s/blockers
/devices/%s/centurion/factory_reset
/devices/%s/centurion/firmware_info
/devices/%s/centurion/hardware_info
/devices/%s/centurion/serial_number
/devices/%s/centurion/uptime
/devices/%s/donotdisturb_state
/devices/%s/driver_info
/devices/%s/given_name
/devices/%s/individuality
/devices/%s/info
/devices/%s/interface/list
/devices/%s/memfault_info
/devices/%s/onboard_given_name
/devices/%s/persistent_data
/devices/%s/slots/state
/devices/compatible_receivers
/devices/info/for_container_id
/devices/interface/list/pending
/devices/list
/devices/list/known
/devices/list/simplified
/devices/model/info
/devices/notification

/devices/pairable
/devices/parent_state/changed
/devices/resources
/devices/state/activated
/devices/state/changed
/devices/state/deactivated
/devices/subdevices/list

/dfu/dismiss
/dfu/progress
/dfu/start

/disable_key/%s/disable
/disable_key/%s/disabled
/disable_key/%s/enable
/disable_key/%s/enable_all
/disable_key/%s/info

/dual_clutch/%s/settings
/dual_clutch/%s/settings/changed

/force_feedback/%s/aperture
/force_feedback/%s/global_damping
/force_feedback/%s/operating_range

/gaming_attachments/%s/changed
/gaming_attachments/%s/current
/gaming_attachments/%s/supported

/hidio/%s/raw_input_report

/hosts_info/%s/ble
/hosts_info/%s/bluetooth
/hosts_info/%s/current
/hosts_info/%s/remove

/illumination_light/%s/color_range
/illumination_light/%s/color_settings
/illumination_light/%s/power_settings
/illumination_light/action
/illumination_light/enable_preset

/input/%s/cid_map
/input/%s/fkc/enabled
/input/%s/fkc/toggle_keys
/input/%s/fkc/trigger_notify
/input/%s/fn_inversion
/input/%s/fn_inversion/changed
/input/%s/mstate
/input/event
/input/mstate/changed

/keyboard/%s/controls/disabled
/keyboard/%s/game_mode
/keyboard/%s/game_mode/capabilities
/keyboard/%s/game_mode/power_on
/keyboard/%s/game_mode/power_on/capabilities

/legacy_profiles_exist

/lighting/%s/brightness
/lighting/%s/cache/reset
/lighting/%s/custom/effect/save
/lighting/%s/custom/effects
/lighting/%s/firmware/action
/lighting/%s/firmware/active_dimming
/lighting/%s/firmware/battery/warning
/lighting/%s/firmware/brightness
/lighting/%s/firmware/cycle_brightness
/lighting/%s/firmware/effects
/lighting/%s/firmware/illumination
/lighting/%s/firmware/indicator
/lighting/%s/firmware/off_ramp
/lighting/%s/firmware/shutdown
/lighting/%s/firmware/startup
/lighting/%s/keep_alive
/lighting/%s/low_battery
/lighting/%s/low_battery/dismiss
/lighting/%s/master_switch_on
/lighting/%s/mode
/lighting/%s/mode/wake
/lighting/%s/power_saving
/lighting/%s/state

/microphone/%s/automatic_gain_control
/microphone/%s/mode
/microphone/%s/mute
/microphone/%s/polar_pattern
/microphone/%s/test/event/state_changed
/microphone/%s/test/get_state
/microphone/%s/test/reset
/microphone/%s/test/standby
/microphone/%s/test/start_playback
/microphone/%s/test/start_record
/microphone/%s/test/stop_playback
/microphone/%s/test/stop_record
/microphone/%s/volume
/microphone/mode/changed
/microphone/polar_pattern/changed

/migrate_lgs_profiles
/migration_progress

/mouse/%s/active_correction
/mouse/%s/angle_snapping
/mouse/%s/dpi
/mouse/%s/dpi_always_on
/mouse/%s/dpi_correction
/mouse/%s/dpi_corrections
/mouse/%s/dpi_lighting_refresh
/mouse/%s/dpi_shift
/mouse/%s/dpi_table
/mouse/%s/dpi_tune/factory
/mouse/%s/dpi_tune/finished
/mouse/%s/dpi_tune/progress
/mouse/%s/dpi_tune/restore
/mouse/%s/dpi_tune/start
/mouse/%s/dpi_tune/stop
/mouse/%s/hybrid_engine
/mouse/%s/info
/mouse/%s/mode_status
/mouse/%s/report_rate
/mouse/%s/report_rate_list
/mouse/%s/sensitivity
/mouse/dpi
/mouse/dpi_cycle
/mouse/dpi_default
/mouse/dpi_down
/mouse/dpi_go_to_shift
/mouse/dpi_shift
/mouse/dpi_up

/multibattery/%s/%s/state

/onboard_profiles/%s/active_profile
/onboard_profiles/%s/disable_profile
/onboard_profiles/%s/edit_profile
/onboard_profiles/%s/enable_profile
/onboard_profiles/%s/onboard_mode
/onboard_profiles/%s/profile
/onboard_profiles/%s/profiles
/onboard_profiles/%s/restore_default_profile
/onboard_profiles/%s/restore_defaults

/pedals/%s/brake_force/changed
/pedals/%s/legacy_settings_for
/pedals/%s/onboard_profile
/pedals/%s/pedal_settings
/pedals/%s/status

/profile/active
/profile/active/changed
/profile/effective
/profile/export
/profile/impacted_profiles_and_slots
/profile/import
/profile/persistent
/profile/prepare_for_publish
/profile/refresh
/profile/remove_by_app
/profile/script_id
/profiles/audio_sample_depot_info
/profiles/persistent_features
/profiles/play_audio_preset
/profiles/play_audio_sample_action
/profiles/reset_audio_preset
/profiles/update

/receivers/compatible_devices
/receivers/info
/receivers/interface/list
/receivers/list
/receivers/pair
/receivers/state/activated
/receivers/state/changed
/receivers/state/deactivated

/rpm_indicator/%s/capabilities
/rpm_indicator/%s/leds
/rpm_indicator/%s/mode
/rpm_indicator/%s/mode_list
/rpm_indicator/%s/rpm
/rpm_led_pattern/%s/info
/rpm_led_pattern/%s/name
/rpm_led_pattern/%s/pattern

/subdevices/%s/change
/subdevices/%s/discover
/subdevices/%s/enable_hub
/subdevices/%s/info
/subdevices/%s/subdevice

/surface_tuning/%s/abort
/surface_tuning/%s/active
/surface_tuning/%s/event
/surface_tuning/%s/save
/surface_tuning/%s/start
/surface_tuning/%s/surface
/surface_tuning/%s/surfaces

/trigger_event

/trueforce/%s/settings
/trueforce/settings

/uvc/%s/camera/settings
/uvc/%s/capabilities
/uvc/%s/global/settings
/uvc/%s/video/settings

/webcam/%s/orientation

/wheel/%s/calibration/center_position
/wheel/%s/calibration/current_position
/wheel/%s/legacy_settings_for
/wheel/%s/onboard_profile
/wheel/%s/paddles_settings
/wheel/%s/rpm_pattern_settings
/wheel/%s/wheel_settings

/wireless/%s/force_pairing/address
/wireless/%s/report_rate
```