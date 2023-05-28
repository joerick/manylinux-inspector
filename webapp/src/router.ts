import { createRouter, createWebHashHistory } from "vue-router";
import Standards from "./views/Standards.vue";
import Version from "./views/Version.vue";
import Standard from "./views/Standard.vue";
import Grid from "./views/Grid.vue";
import NotFound from "./views/NotFound.vue";

const router = createRouter({
    history: createWebHashHistory(),
    routes: [
        { path: '/', name: 'grid', component: Grid },
        { path: '/standards', name: 'standards', component: Standards },
        { path: '/:name', name: 'standard', component: Standard},
        { path: '/:name/:tag', name: 'version', component: Version },
        // 404
        { path: '/:pathMatch(.*)*', component: NotFound },
    ],
})

export default router;
