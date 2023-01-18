<script setup>
import Footer from "@/components/footer.vue";
</script>

<template>
  <v-app id="app">
    <!-- <v-navigation-drawer>...</v-navigation-drawer> -->
    <v-app-bar title="XAI as a Service" :elevation="6"></v-app-bar>
    <v-main>
      <v-navigation-drawer
        permanent
        location="left"
        :elevation="4"
        :rail="rail"
        @click="rail = false"
        width="200"
      >
        <!-- <template v-slot:prepend> -->
        <v-list-item
          lines="two"
          prepend-avatar="https://randomuser.me/api/portraits/women/81.jpg"
          title="Jane Smith"
          subtitle="Logged in"
          nav
        >
          <template v-slot:append>
            <v-btn
              variant="text"
              icon="mdi-chevron-left"
              @click.stop="rail = !rail"
            ></v-btn>
          </template>
        </v-list-item>
        <!-- </template> -->

        <!-- <v-divider></v-divider> -->

        <v-list density="compact" nav>
          <v-list-item
            v-for="tab in tabList"
            :key="tab.title"
            :prepend-icon="tab.icon"
            :title="tab.title"
            @click="clickTab(tab.title)"
            :active="checkIsCurrentTab(tab.title)"
            class="unselectable"
          ></v-list-item>
        </v-list>
      </v-navigation-drawer>

      <div class="mainPanel">
        <!-- <ServiceView class="view"></ServiceView>
        <TaskSheetView class="view"></TaskSheetView>
        <PipelineView class="view"></PipelineView> -->
        <router-view v-slot="{ Component }" :elevation="4">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
        <Footer style="margin-top: 0.5em"></Footer>
      </div>
    </v-main>
  </v-app>
</template>

<script>
const tabList = [
  {
    icon: "mdi-server",
    title: "Service",
    path: "/",
  },
  {
    icon: "mdi-file-table-outline",
    title: "Task Sheet",
    path: "/task_sheet",
  },
  {
    icon: "mdi-pipe",
    title: "Pipeline",
    path: "/pipeline",
  },
  {
    icon: "mdi-graphql",
    title: "Provenance",
    path: "/provenance",
  },
];

export default {
  data: () => ({
    tabList,
    rail: false,
    currentTab: "",
  }),
  mounted: function () {
    let sp = window.location.href.split("/");
    let path = "/" + sp[sp.length - 1];
    let tab = "";
    for (const i of tabList) {
      if (path === i.path) {
        tab = i.title;
      }
    }
    this.clickTab(tab);
  },
  methods: {
    findPathByTab(tab) {
      let target = undefined;
      for (const tabItem of this.tabList) {
        if (tabItem.title === tab) {
          target = tabItem;
        }
      }
      return target;
    },
    clickTab(tab) {
      // console.log(tab);
      this.currentTab = tab;
      let tabItem = this.findPathByTab(tab);
      this.$router.push(`${tabItem.path}`);
    },
    checkIsCurrentTab(targetTab) {
      return targetTab === this.currentTab;
    },
  },
};
</script>

<style scoped>
.mainPanel {
  height: 100%;
  padding: 1.2em 1.2em 3em 1.2em;
}

.view {
  height: 100%;
  /* position: absolute; */
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s;
}

.fade-enter,
.fade-leave-to {
  opacity: 0;
}

.slide-fade-enter-active {
  transition: all 0.3s ease;
}
.slide-fade-leave-active {
  transition: all 0.3s ease;
}
.slide-fade-enter, .slide-fade-leave-to
/* .slide-fade-leave-active for below version 2.1.8 */ {
  /* right: -10%; */
  transform: translateX(-10px);
  opacity: 0;
}

.slide-r-fade-enter-active {
  transition: all 0.3s ease;
}
.slide-r-fade-leave-active {
  transition: all 0.3s ease;
}
.slide-r-fade-enter, .slide-r-fade-leave-to
/* .slide-fade-leave-active for below version 2.1.8 */ {
  /* right: -10%; */
  transform: translateX(10px);
  opacity: 0;
}

.small-slide-r-fade-enter-active {
  transition: all 0.3s ease;
}
.small-slide-r-fade-leave-active {
  transition: all 0.3s ease;
}
.small-slide-r-fade-enter, .small-slide-r-fade-leave-to
/* .slide-fade-leave-active for below version 2.1.8 */ {
  /* right: -10%; */
  transform: translateX(3px);
  opacity: 0;
}
</style>

<style>
@import "../src/assets/css/index.less";
.trHover {
  transition: all 0.5s !important;
  cursor: pointer;
}
.trHover:hover {
  background-color: rgba(219, 219, 219, 0.627);
}
</style>
