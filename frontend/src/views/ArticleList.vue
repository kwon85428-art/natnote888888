<script setup lang="ts">
import { ref } from 'vue'
import ArticleListRow from '@/components/article/ArticleListRow.vue'
import ArticleCategoryDock from '@/components/article/ArticleCategoryDock.vue'
import ArticleCategoryTabs from '@/components/article/ArticleCategoryTabs.vue'
import ArticleCategorySidebar from '@/components/article/ArticleCategorySidebar.vue'
import HomeArticlesSection from '@/components/home/HomeArticlesSection.vue'
import HomeFeaturedBlock from '@/components/home/HomeFeaturedBlock.vue'
import PublicNav from '@/components/PublicNav.vue'
import PlatformFooter from '@/components/PlatformFooter.vue'
import { useArticleListPage } from '@/composables/useArticleListPage'
import { useArticlePagePromoted } from '@/composables/useArticlePagePromoted'
import { trackSiteVisit } from '@/api/public'
import type { SiteItem } from '@/types/models'
import '@/styles/article/page.css'
import '@/styles/article/global.css'
import '@/styles/home/page.css'

const {
  categories,
  list,
  total,
  filter,
  drawerVisible,
  articleNavCollapsed,
  currentPage,
  pageSize,
  currentCategoryLabel,
  resolveCatIcon,
  catNavTitle,
  onFilterChange,
  onPageChange,
  toggleArticleNavCollapsed,
} = useArticleListPage()

const {
  promotedSites,
  promotedArticles,
  showPromotedSites,
  showPromotedArticles,
  showAny,
  loadError: promotedLoadError,
} = useArticlePagePromoted()

const dockCmp = ref<InstanceType<typeof ArticleCategoryDock> | null>(null)
const tabsCmp = ref<InstanceType<typeof ArticleCategoryTabs> | null>(null)

function onSelectFilter(val: string) {
  onFilterChange(val, {
    dockScrollEl: dockCmp.value?.dockScrollRef ?? null,
    tabScrollEl: tabsCmp.value?.tabScrollRef ?? null,
  })
}

async function openSite(site: SiteItem) {
  try {
    await trackSiteVisit(site.id)
  } catch {
    /* ignore */
  }
}
</script>

<template>
  <PublicNav />

  <main class="home article-page">
    <div class="home__workspace">
      <el-alert
        v-if="promotedLoadError"
        class="home-load-error"
        type="warning"
        :title="promotedLoadError"
        show-icon
        :closable="false"
      />

      <div id="article-main" class="shell public-main-shell">
        <div class="split" :class="{ 'split--cat-collapsed': articleNavCollapsed }">
          <ArticleCategorySidebar
            v-if="categories.length"
            :categories="categories"
            :filter="filter"
            :collapsed="articleNavCollapsed"
            :resolve-icon="resolveCatIcon"
            :cat-nav-title="catNavTitle"
            @select="onSelectFilter"
            @toggle-collapsed="toggleArticleNavCollapsed"
          />

          <div class="split__main" aria-label="文章与推荐">
            <div v-if="showAny" class="promoted-stack">
              <HomeArticlesSection
                v-if="showPromotedArticles && promotedArticles.length"
                :articles="promotedArticles"
                hide-more
              />
              <HomeFeaturedBlock
                v-if="showPromotedSites && promotedSites.length"
                :sites="promotedSites"
                @open-site="openSite"
              />
            </div>

            <section id="article-list-panel" class="article-list-panel" aria-label="文章列表">
              <ArticleCategoryTabs
                v-if="categories.length"
                ref="tabsCmp"
                :categories="categories"
                :filter="filter"
                :resolve-icon="resolveCatIcon"
                @select="onSelectFilter"
              />

              <div
                class="article-tab-panel"
                role="tabpanel"
                :aria-label="currentCategoryLabel()"
              >
                <div v-if="list.length" class="article-list">
                  <ArticleListRow v-for="n in list" :key="n.id" :article="n" />
                </div>
                <el-empty v-else description="暂无文章" />

                <div v-if="total > 0" class="pagination-bar">
                  <el-pagination
                    background
                    layout="total, prev, pager, next, jumper"
                    :total="total"
                    :page-size="pageSize"
                    :current-page="currentPage"
                    :hide-on-single-page="false"
                    @current-change="onPageChange"
                  />
                </div>
              </div>
            </section>
          </div>
        </div>
      </div>
    </div>

    <ArticleCategoryDock
      ref="dockCmp"
      :categories="categories"
      :filter="filter"
      :current-label="currentCategoryLabel()"
      :drawer-visible="drawerVisible"
      :resolve-icon="resolveCatIcon"
      @update:drawer-visible="drawerVisible = $event"
      @select="onSelectFilter"
    />

    <PlatformFooter />
  </main>
</template>
