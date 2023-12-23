import { createRouter, createWebHashHistory } from "vue-router";
import HomeView from "../views/HomeView.vue";

const router = createRouter({
    routes: [
        {
            name: "Home",
            path: "/",
            component: HomeView,
        },
        {
            name: "Test",
            path: "/test",
            component: () => import("../views/TestView.vue"),
        },
        {
            name: "Portfolio",
            path: "/portfolio",
            component: () => import("../views/PortfolioView.vue"),
        },
        {
            name: "Prestaties",
            path: "/prestaties",
            component: HomeView,
        },
        {
            name: "Acties",
            path: "/actions",
            component: () => import("../views/ActionsView.vue"),
        },
        {
            name: "Settings",
            path: "/settings",
            component: () => import("../views/SettingView.vue"),
            children: [
                {
                    name: "Settings Profile",
                    path: "/settings/profile",
                    component: () => import("../views/SettingsViewProfile.vue"),
                    meta: {
                        displayName: "Profile",
                    },
                },
                {
                    name: "Settings Tickers",
                    path: "/settings/ticker",
                    component: () => import("../views/SettingsViewTicker.vue"),
                    meta: {
                        displayName: "Tickers",
                    },
                },
            ],
        },
    ],
    history: createWebHashHistory(),
});

export default router;
