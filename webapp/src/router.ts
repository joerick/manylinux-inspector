import { createRouter, createWebHashHistory } from "vue-router";
import Grid2 from "./views/Grid2.vue";
import Raw from "./views/Raw.vue";

const router = createRouter({
    history: createWebHashHistory(),
    routes: [
        { path: '/', component: Grid2 },
        { path: '/raw', component: Raw },
    ],
})

export default router;
