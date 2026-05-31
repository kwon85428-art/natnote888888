import type { PlatformSettings } from '@/types/models'

export const PLATFORM_SETTINGS_UPDATED = 'platform-settings-updated'

export function dispatchPlatformSettingsUpdated(settings: PlatformSettings) {
  window.dispatchEvent(
    new CustomEvent<PlatformSettings>(PLATFORM_SETTINGS_UPDATED, { detail: settings }),
  )
}
