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
        },
        {
            name: "Test",
            path: "/test",
            component: () => import('../views/TestView.vue')
        },
        {
            name: "Portfolio",
            path: '/portfolio',
            component: () => import('../views/PortfolioView.vue')
        },
        {
            name: "Prestaties",
            path: '/prestaties',
            component: HomeView
        }
    ],
    history: createWebHashHistory(),
});

export default router;
