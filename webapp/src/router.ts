import { createRouter, createWebHashHistory } from "vue-router";
import Grid from "./views/Grid.vue";
import Raw from "./views/Raw.vue";

const router = createRouter({
    history: createWebHashHistory(),
    routes: [
        { path: '/', component: Grid },
        { path: '/raw', component: Raw },
    ],
})

export default router;
