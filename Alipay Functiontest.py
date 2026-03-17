def alipay_login(page):
    try:
        print("🔄 Redirecting to Alipay login page...")

        # Check if the first selector is available
        alipay_button = page.query_selector("#thirdpart-login > a.thirdpart-login-btn.btn-alipay > i")
        if alipay_button:
            print("✔️ Alipay button found, clicking...")
            page.click("#thirdpart-login > a.thirdpart-login-btn.btn-alipay > i")
        else:
            print("❌ First selector not found, checking for the alternative selector...")
            # Check for the second selector
            alipay_button = page.query_selector("#thirdpart-login > a.thirdpart-login-btn.btn-alipay")
            if alipay_button:
                print("✔️ Alipay button found using the alternative selector, clicking...")
                page.click("#thirdpart-login > a.thirdpart-login-btn.btn-alipay")
            else:
                print("❌ Alipay button not found using any of the selectors.")
                return None

        time.sleep(10)

        # Wait for the slider to appear (with a 40 seconds timeout)
        try:
            page.wait_for_selector("#baxia-punish > div.wrapper > div > div.bannar > div.captcha-tips", timeout=20000)  # Wait for slider to appear
            print("🧩 Slider detected, attempting to solve...")
            solve_slider_if_present(page)
        except Exception:
            print("✅ No slider found, continuing...")

        # Wait for the QR code canvas to appear (with a 40 seconds timeout)
        try:
            page.wait_for_selector("#J-barcode-container > canvas", timeout=40000)  # Wait for QR code canvas
            qr_canvas = page.query_selector("#J-barcode-container > canvas")
            if not qr_canvas:
                print("❌ Alipay QR code canvas not found.")
                return None

            # Display QR code
            qr_image = qr_canvas.screenshot()
            img = Image.open(io.BytesIO(qr_image))
            img.show()
            print("📱 Scan QR with Alipay app to proceed...")

        except Exception:
            print("❌ Timeout or error while waiting for QR code.")

        return wait_for_login_success(page)

    except Exception as e:
        print("❌ Alipay login error:", e)
        print("⚠️ Check your network connection.")
        return None
def solve_slider_if_present(page):
    try:
        slider = page.query_selector(".nc-slide-btn")
        if not slider:
            print("❌ Slider not found.")
            return False

        # Solve the slider by simulating the drag
        box = slider.bounding_box()
        print("🧩 Solving slider...")
        page.mouse.move(box["x"] + 5, box["y"] + box["height"] / 2)
        page.mouse.down()
        page.mouse.move(box["x"] + 300, box["y"] + box["height"] / 2, steps=30)
        page.mouse.up()
        time.sleep(3)
        return True

    except Exception as e:
        print("⚠️ Slider solving failed:", e)
    return False
   