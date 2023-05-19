import { defineStore } from "pinia";

interface stateType {
    loading: boolean,
    userid: string | null
}

export const useMain = defineStore("Main", {
    state(): stateType {
        return {
            loading: false,
            userid: null,
        };
    },
    getters: {
        isLoading(state): boolean {
            return state.loading
        },
        getUserId(state): string | null { 
            return state.userid
        }
    },
    actions: {
        setLoading(modus: boolean | null = null) {
            if(modus === null) {
                this.loading = !this.loading
            } else {
                this.loading = modus
            }
        },
        setUserId(uuid: string | null) {
            this.userid = uuid
        }
    },
    persist: true
});