<template>
    <div class="my-10 flex gap-5">
        <div class="w-1/6">
            <RouterLink
                v-for="_route in routes"
                :to="_route"
                class="my-3 flex w-full gap-3 rounded-md bg-slate-100 px-2 py-2 text-left font-bold text-blue-900"
            >
                <span class="w-1/12"><UserCircle /></span
                ><span> {{ _route.meta?.displayName }}</span>
            </RouterLink>
        </div>
        <div class="w-full">
            <RouterView />
        </div>
    </div>
</template>

<script setup lang="ts">
import { UserCircle } from "lucide-vue-next";
import { computed, onMounted, ref, watch } from "vue";
import { useRoute, useRouter, RouteLocationNormalizedLoaded } from "vue-router";

const router = useRouter();
const route = useRoute();

const routes = computed(() => {
    return route.matched.filter((el) => el.path === "/settings")[0].children;
});

onMounted(() => {
    router.push({
        name: "Settings Profile",
    });
});

watch(route, (newVal: RouteLocationNormalizedLoaded) => {
    if (newVal.path === "/settings") {
        router.push({
            name: "Settings Profile",
        });
    }
});
</script>
