import { createApp } from "vue";
import App from "@/App.vue";
import ax from "@/plugins/axios-helper";
import router from "@/router";

const vueMap = new Map();

// Vuetify
import "@mdi/font/css/materialdesignicons.css"; // Ensure you are using css-loader
import "vuetify/styles";
import { createVuetify } from "vuetify";
import * as components from "vuetify/components";
import * as directives from "vuetify/directives";

const vuetify = createVuetify({
  components,
  directives,
});

createApp(App)
  .use(vuetify)
  .use(router)
  .mixin({
    data: function () {
      return {
        vueMap,
        mapKey: "",
        // config,
        ax,
      };
    },
    mounted: function () {
      // 方便在任意组件访问其他组件
      if (this.$el.id !== undefined && this.$el.id !== "") {
        this.vueMap.set(this.$el.id, this);
        this.mapKey = this.$el.id;
      }
      this.ax.universalErrorHandler = (error) => {
        if (String(error.message) === "Network Error")
          this.errorToast("Server is down");
      };
    },
    methods: {},
  })
  .mount("#app");
