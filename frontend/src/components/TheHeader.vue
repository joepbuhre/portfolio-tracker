<template>
    <header class="sticky top-0 bg-white">
        <nav class="flex gap-20 px-10 py-2 shadow-md">
            <div class="" v-for="loc in routes">
                <RouterLink :to="loc">
                    {{ loc.name }}
                </RouterLink>
            </div>
            <button class="fixed right-2 top-2 flex gap-2" @click="logout">
                <LogOutIcon />
                Logout
            </button>
        </nav>
    </header>
</template>
<script setup lang="ts">
import { ref } from "vue";
import { RouteLocationNamedRaw, RouteLocationRaw } from "vue-router";
import { LogOutIcon } from "lucide-vue-next";
import { useMain } from "../store/main";
import TheLoginModel from "./TheLoginModel.vue";

const main = useMain();

const logout = () => {
    main.setUserId(null);
};

const routes = ref<RouteLocationNamedRaw[]>([
    {
        name: "Home",
    },
    {
        name: "Portfolio",
    },
    {
        name: "Prestaties",
    },
    {
        name: "Acties",
    },
    {
        name: "Settings",
    },
]);
</script>
