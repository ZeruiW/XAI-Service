<script setup>
import Footer from "./components/footer.vue";
</script>

<template>
  <v-app>
    <!-- <v-navigation-drawer>...</v-navigation-drawer> -->
    <v-app-bar title="XAI as a Service" :elevation="2"></v-app-bar>
    <v-main>
      <v-navigation-drawer permanent location="left">
        <template v-slot:prepend>
          <v-list-item
            lines="two"
            prepend-avatar="https://randomuser.me/api/portraits/women/81.jpg"
            title="Jane Smith"
            subtitle="Logged in"
          ></v-list-item>
        </template>

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
      <!-- <Footer></Footer> -->
    </v-main>
  </v-app>
</template>

<script>
const tabList = [
  {
    icon: "mdi-home-city",
    title: "Service",
  },
  {
    icon: "mdi-account",
    title: "Task Sheet",
  },
  {
    icon: "mdi-account-group-outline",
    title: "Pipeline",
  },
];

export default {
  data: () => ({
    tabList,
    currentTab: tabList[0].title,
  }),
  mounted: function () {},
  methods: {
    clickTab(tab) {
      console.log(tab);
      this.currentTab = tab;
    },
    checkIsCurrentTab(targetTab) {
      return targetTab === this.currentTab;
    },
  },
};
</script>

<style scoped>
.logo {
  height: 6em;
  padding: 1.5em;
  will-change: filter;
}
.logo:hover {
  filter: drop-shadow(0 0 2em #646cffaa);
}
.logo.vue:hover {
  filter: drop-shadow(0 0 2em #42b883aa);
}
</style>

<style>
@import "../src/assets/css/index.less";
</style>
