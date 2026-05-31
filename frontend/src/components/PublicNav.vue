<script setup lang="ts">
import { usePublicNav } from '@/composables/usePublicNav'

defineProps<{ subtitle?: string }>()

const {
  logoSrc,
  showSitesNav,
  showArticlesNav,
  menuSitesLabel,
  menuArticlesLabel,
  displayBrand,
  isSites,
  isArticles,
  onLogoError,
  go,
} = usePublicNav()
</script>

<template>
  <header class="pub-nav">
    <div class="pub-nav__inner">
      <div class="pub-nav__brand" @click="go('/')">
        <span class="pub-nav__logo-wrap">
          <img
            class="pub-nav__logo"
            :src="logoSrc"
            width="32"
            height="32"
            alt=""
            @error="onLogoError"
          />
        </span>
        <div class="pub-nav__titles">
          <span class="pub-nav__name">{{ displayBrand }}</span>
          <span v-if="subtitle" class="pub-nav__sub">{{ subtitle }}</span>
        </div>
      </div>
      <nav class="pub-nav__links" aria-label="主导航">
        <button v-if="showSitesNav" type="button" class="nav-link" :class="{ active: isSites }" @click="go('/sites')">
          {{ menuSitesLabel }}
        </button>
        <button v-if="showArticlesNav" type="button" class="nav-link" :class="{ active: isArticles }" @click="go('/articles')">
          {{ menuArticlesLabel }}
        </button>
      </nav>
    </div>
  </header>
</template>

<style scoped>
.pub-nav {
  position: sticky;
  top: 0;
  z-index: 50;
  background: rgba(255, 255, 255, 0.88);
  backdrop-filter: blur(14px) saturate(1.2);
  -webkit-backdrop-filter: blur(14px) saturate(1.2);
  border-bottom: 1px solid var(--nav-border);
  box-shadow:
    0 1px 0 rgba(255, 255, 255, 0.9),
    0 4px 16px rgba(15, 23, 42, 0.04);
}

.pub-nav__inner {
  max-width: var(--content-max, 1200px);
  margin: 0 auto;
  padding: 10px var(--pub-content-pad-x);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.pub-nav__brand {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  min-width: 0;
  border-radius: var(--pub-radius-sm, 8px);
  padding: 2px 4px 2px 2px;
  margin: -2px -4px -2px -2px;
  transition: background 0.15s ease;
}

.pub-nav__brand:hover {
  background: rgba(241, 245, 249, 0.85);
}

.pub-nav__logo-wrap {
  display: inline-flex;
  flex-shrink: 0;
  padding: 3px;
  border-radius: 10px;
  background: linear-gradient(145deg, #fff 0%, #f8fafc 100%);
  border: 1px solid var(--border-subtle);
  box-shadow: var(--pub-shadow-sm);
}

.pub-nav__logo {
  display: block;
  border-radius: 7px;
  object-fit: cover;
}

.pub-nav__titles {
  display: flex;
  flex-direction: column;
  gap: 1px;
  min-width: 0;
}

.pub-nav__name {
  font-size: var(--pub-nav-name-size);
  font-weight: 800;
  color: var(--text);
  letter-spacing: -0.03em;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.2;
}

.pub-nav__sub {
  font-size: var(--pub-nav-sub-size);
  color: var(--text-muted);
  line-height: 1.35;
}

.pub-nav__links {
  display: flex;
  gap: 6px;
  flex-shrink: 0;
  padding: 3px;
  border-radius: 999px;
  background: #f1f5f9;
  border: 1px solid var(--border-subtle);
}

.nav-link {
  border: 1px solid transparent;
  background: transparent;
  padding: 8px 16px;
  border-radius: 999px;
  font-size: var(--pub-nav-link-size);
  font-weight: 600;
  color: var(--text-muted);
  cursor: pointer;
  transition:
    background 0.18s ease,
    color 0.18s ease,
    border-color 0.18s ease,
    box-shadow 0.18s ease;
}

.nav-link:hover {
  color: var(--text);
  background: rgba(255, 255, 255, 0.75);
}

.nav-link.active {
  background: var(--surface);
  border-color: var(--accent-muted);
  color: var(--accent);
  box-shadow: 0 2px 10px rgba(37, 99, 235, 0.12);
}

@media (max-width: 560px) {
  .pub-nav__inner {
    padding-top: var(--pub-content-pad-top);
    padding-bottom: var(--pub-content-pad-top);
  }

  .nav-link {
    padding: 7px 12px;
    /* 保持与 --pub-nav-link-size 一致，避免极窄屏反而缩小主导航字 */
    font-size: var(--pub-nav-link-size);
  }

  .pub-nav__links {
    gap: 4px;
    padding: 2px;
  }
}
</style>
