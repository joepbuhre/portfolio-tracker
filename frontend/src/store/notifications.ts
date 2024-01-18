import { NotificationType } from "@src/enums/Notification";
import { StoreDefinition, defineStore } from "pinia";

interface IuNotification {
    id: string;
    text: string;
    type: NotificationType;
    delete: () => void;
}

export const useNotifications = defineStore("Notifications", {
    state: (): {
        notifications: {
            [key: string]: IuNotification;
        };
    } => {
        return {
            notifications: {},
        };
    },
    getters: {
        get(state) {
            return state.notifications;
        },
    },
    actions: {
        add(
            text: string,
            type: NotificationType = NotificationType.Success,
            timeout: number = 10000,
        ) {
            const randId = `ID${Math.round(Math.random() * 1000).toString()}`;

            this.notifications[randId] = {
                id: randId,
                text: text,
                type: type,
                delete: () => this.delete(randId),
            };

            if (timeout > 0) {
                setTimeout(() => {
                    this.delete(randId);
                }, timeout);
            }
            return this.notifications[randId];
        },
        delete(randId: string | IuNotification) {
            if (typeof randId !== "string") {
                randId = randId.id;
            }
            try {
                delete this.notifications[randId];
            } catch (error) {
                console.log(error);
            }
        },
    },
});
