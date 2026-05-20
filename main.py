import cv2
import random
import time
from hand_tracking import HandTracker

cap = cv2.VideoCapture(0)
tracker = HandTracker()

score = 0
game_over = False
start_time = time.time()

# 🍎 fruits + 💣 bombs
objects = []

def create_object():
    is_bomb = random.random() < 0.2  # 20% bomb
    return {
        "x": random.randint(100, 600),
        "y": 0,
        "speed": random.randint(3, 8),
        "type": "bomb" if is_bomb else "fruit"
    }

# start objects
for _ in range(5):
    objects.append(create_object())

while True:
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape

    finger = tracker.get_index_finger_position(frame)

    # ⏱ difficulty increases over time
    if len(objects) < 10 and time.time() - start_time > 5:
        objects.append(create_object())
        start_time = time.time()

    for obj in objects:
        obj["y"] += obj["speed"]

        color = (0, 0, 255) if obj["type"] == "bomb" else (0, 255, 0)
        cv2.circle(frame, (obj["x"], obj["y"]), 25, color, -1)

        # reset if fall
        if obj["y"] > h:
            obj["y"] = 0
            obj["x"] = random.randint(100, w-100)

        # collision
        if finger:
            fx, fy = finger
            dist = ((fx - obj["x"])**2 + (fy - obj["y"])**2)**0.5

            if dist < 30:
                if obj["type"] == "bomb":
                    game_over = True
                else:
                    score += 1

                obj["y"] = 0
                obj["x"] = random.randint(100, w-100)

    # score
    cv2.putText(frame, f"Score: {score}", (20, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    # game over screen
    if game_over:
        cv2.putText(frame, "GAME OVER", (200, 300),
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 5)

        cv2.imshow("Fruit Ninja AI", frame)
        cv2.waitKey(0)
        break

    cv2.imshow("Fruit Ninja AI", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()