import { createRouter, createWebHistory } from "vue-router";
import Grid from "./views/Grid.vue";

const router = createRouter({
    history: createWebHistory(),
    routes: [
        { path: '/', component: Grid },
    ],
})

export default router;
