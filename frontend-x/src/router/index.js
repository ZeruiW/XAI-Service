import { createRouter, createWebHashHistory } from "vue-router";
import ServiceView from "@/views/ServiceView.vue";

const routes = [
  {
    path: "/",
    name: "Service",
    component: ServiceView,
  },
  {
    path: "/task_sheet",
    name: "TaskSheet",
    component: () => import("@/views/TaskSheetView.vue"),
  },
  {
    path: "/pipeline",
    name: "Pipeline",
    component: () => import("@/views/PipelineView.vue"),
  },
  // {
  //   path: "*",
  //   name: "PageNotFound",
  //   component: () => import("@/views/PageNotFound.vue"),
  // },
];

const router = createRouter({
  history: createWebHashHistory(),
  routes,
});

export default router;
