import { createRouter, createWebHashHistory } from "vue-router";
import Standards from "./views/Standards.vue";
import Version from "./views/Version.vue";
import Grid from "./views/Grid.vue";
import NotFound from "./views/NotFound.vue";

const router = createRouter({
    history: createWebHashHistory(),
    routes: [
        { path: '/', component: Standards },
        { path: '/grid', name: 'grid', component: Grid },
        { path: '/:name/:tag', name: 'version', component: Version },
        // 404
        { path: '/:pathMatch(.*)*', component: NotFound },
    ],
})

export default router;
