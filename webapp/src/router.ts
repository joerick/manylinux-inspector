import { createRouter, createWebHashHistory } from "vue-router";
import Home from "./views/Home.vue";
import Raw from "./views/Raw.vue";

const router = createRouter({
    history: createWebHashHistory(),
    routes: [
        { path: '/', component: Home },
        { path: '/raw', component: Raw },
    ],
})

export default router;
