<script setup lang="ts">
import { ref } from 'vue'
import SiteCategoryDock from '@/components/home/SiteCategoryDock.vue'
import SiteCategorySidebar from '@/components/home/SiteCategorySidebar.vue'
import HomeFeaturedBlock from '@/components/home/HomeFeaturedBlock.vue'
import HomeArticlesSection from '@/components/home/HomeArticlesSection.vue'
import SiteCatalog from '@/components/home/SiteCatalog.vue'
import PublicNav from '@/components/PublicNav.vue'
import PlatformFooter from '@/components/PlatformFooter.vue'
import { useSitesHomePage } from '@/composables/useSitesHomePage'
import '@/styles/home/page.css'
import '@/styles/home/global.css'

const {
  platformBundle,
  siteCategories,
  sitesByCategory,
  promotedSites,
  promotedArticles,
  showPromotedSites,
  showPromotedArticles,
  loading,
  loadError,
  activeSiteCatId,
  siteNavCollapsed,
  catDrawerVisible,
  resolveCatIcon,
  currentSiteCategoryName,
  siteCatNavTitle,
  scrollToSiteCategory,
  selectCatFromDrawer,
  toggleSiteNavCollapsed,
  openSite,
} = useSitesHomePage()

const dockCmp = ref<InstanceType<typeof SiteCategoryDock> | null>(null)

function onSelectSiteCat(id: number) {
  scrollToSiteCategory(id, dockCmp.value?.dockScrollRef ?? null)
}

function onSelectFromDrawer(c: { id: number }) {
  selectCatFromDrawer(c, dockCmp.value?.dockScrollRef ?? null)
}
</script>

<template>
  <PublicNav />

  <main class="home">
    <div class="home__workspace">
      <el-alert
        v-if="loadError"
        class="home-load-error"
        type="warning"
        :title="loadError"
        show-icon
        :closable="false"
      />
      <div id="home-main" class="shell public-main-shell">
        <div class="split" :class="{ 'split--cat-collapsed': siteNavCollapsed }" v-loading="loading">
          <SiteCategorySidebar
            :categories="siteCategories"
            :active-id="activeSiteCatId"
            :collapsed="siteNavCollapsed"
            :resolve-icon="resolveCatIcon"
            :nav-title="siteCatNavTitle"
            @select="onSelectSiteCat"
            @toggle-collapsed="toggleSiteNavCollapsed"
          />

          <div class="split__main" aria-label="网址与推荐">
            <div
              v-if="
                (showPromotedArticles && promotedArticles.length) ||
                (showPromotedSites && promotedSites.length)
              "
              class="promoted-stack"
            >
              <HomeArticlesSection
                v-if="showPromotedArticles && promotedArticles.length"
                :articles="promotedArticles"
              />

              <HomeFeaturedBlock
                v-if="showPromotedSites && promotedSites.length"
                :sites="promotedSites"
                hide-more
                @open-site="openSite"
              />
            </div>

            <SiteCatalog
              :categories="siteCategories"
              :sites-by-category="sitesByCategory"
              :resolve-icon="resolveCatIcon"
              @open-site="openSite"
            />
          </div>
        </div>
      </div>
    </div>

    <PlatformFooter v-if="platformBundle" :prefetch="platformBundle" />

    <SiteCategoryDock
      v-if="siteCategories.length && !loading"
      ref="dockCmp"
      :categories="siteCategories"
      :active-id="activeSiteCatId"
      :current-label="currentSiteCategoryName()"
      :drawer-visible="catDrawerVisible"
      :resolve-icon="resolveCatIcon"
      @update:drawer-visible="catDrawerVisible = $event"
      @select="onSelectSiteCat"
      @select-from-drawer="onSelectFromDrawer"
    />
  </main>
</template>
