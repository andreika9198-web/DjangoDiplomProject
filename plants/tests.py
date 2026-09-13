import cv2

print("=== Визуальный тест камер ===")
print("Нажми любую клавишу для переключения между камерами")
print("Нажми 'q' для выхода")

for i in [0, 1]:
    cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print(f"[{i}] НЕ открылась")
        continue

    ret, frame = cap.read()
    if not ret:
        print(f"[{i}] кадр не получен")
        cap.release()
        continue

    cv2.imshow(f"Camera {i} - press any key", frame)
    print(f"[{i}] Показана камера. Нажми клавишу...")
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    cap.release()

print("=== Готово ===")