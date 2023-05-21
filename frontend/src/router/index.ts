import { createRouter, createWebHashHistory } from "vue-router";
import HomeView from '../views/HomeView.vue'

const router = createRouter({
    routes: [
        {
            name: "Home",
            path: "/",
            component: HomeView,
        },
        {
            name: "Match Tickers",
            path: "/match-tickers",
            component: () => import('../views/MatchTickerView.vue')
        }
    ],
    history: createWebHashHistory(),
});

export default router;
