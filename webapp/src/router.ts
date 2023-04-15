import { createRouter, createWebHashHistory } from "vue-router";
import Standards from "./views/Standards.vue";
import Grid from "./views/Grid.vue";

const router = createRouter({
    history: createWebHashHistory(),
    routes: [
        { path: '/', component: Standards },
        { path: '/grid', component: Grid },
        { path: '/:name', name: 'standard', component: Standards },
    ],
})

export default router;
