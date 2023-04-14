import { createRouter, createWebHashHistory } from "vue-router";
import Grid from "./views/Grid.vue";

const router = createRouter({
    history: createWebHashHistory(),
    routes: [
        { path: '/', component: Grid },
    ],
})

export default router;
