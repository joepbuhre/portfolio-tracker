import { createRouter, createWebHashHistory } from "vue-router";
import HomeView from '../views/HomeView.vue'

const router = createRouter({
    routes: [
        {
            name: "Home",
            path: "/",
            component: HomeView,
        },
    ],
    history: createWebHashHistory(),
});

export default router;
