<div class="header" align="center">
    <h2>
        <a href="https://www.youtube.com/channel/UCpY10pb4-S0PwCJBp2r6nOvg" title="temp">
            <img alt="" src="https://yt3.ggpht.com/a/AATXAJyqMS98UZ8kCtNAyGD1NUPd4irEZQbl-SvW32JcgQ=s288-c-k-c0xffffffff-no-rj-mo" width="100px" height="100px" />
        </a>
        <br />
        Taste like Developer
    </h2>
    <p align="center">:octocat: home-assistant-tips: zigbee</p>
</div>

---

### Overview
라즈베리파이에 홈어시스턴트를 사용하고 있다면, 직비 수신 모듈을 달아서 각종 직비 센서 연동을 할 수 있다. 모든 내용은 오피셜 도큐먼트를 참조하였으며, 업데이트에 따라서 메뉴얼이 조금씩 달라질 수 있기때문에, 오피셜 도큐먼트의 링크와 해당 부분에대한 간략한 노트를 남기는 방식으로 정리하였다.

### Prerequisite
subscribe [Taste like Developer](https://www.youtube.com/channel/UCpY9pb4-S0PwCJBp2r6nOvg)

첫번쨰 문서인 [README.md](https://github.com/devtaste/home-assistant-tips)에서 다루었던 문서를 먼저 읽어서 홈어시스턴트에 대한 전반적인 감을 익힌 후에 시작하면 좋을것 같다.

### Contributor(s)
- **Taste like Developer** - [Youtube](https://www.youtube.com/channel/UCpY9pb4-S0PwCJBp2r6nOvg)

### Contents

* 라즈베리파이(홈어시스턴트) 와 연동가능한 [Zigbee 수신 usb 모듈 리스트](https://www.zigbee2mqtt.io/information/supported_adapters.html).

목록의 리스트 중 CC2531이 가장 저렴하고, 구매하기도 쉽다(알리익스프레스). 하지만 가장 저렴한 만큼 수신거리에 길지는 않다. 집 구조가 복잡하거나 장애물로 많이 막혀있다면, 가장 강력한 ConBee2 모델을 추천한다. 만약 CC2531 모델을 사용한다면, 구매한 상태 그대로 사용하는것이 아니라 [펌웨어를 입혀줘야한다](https://www.zigbee2mqtt.io/information/flashing_the_cc2531.html).
따라서 추가적으로 CC debugger와 CC2531 downloader cable를 함께 구매하면 좋다. 모두 다 합쳐도 여전히 10불 아래로 저렴하다.

* 라즈베리파이와 연결.

직비 수신 usb 모듈을 라즈베리파이와 직접 연결해도 잘 동작하지만, usb 연장 케이블을 통해 조금 더 높은 위치에 떨어뜨려 놓으면, 라디오 신호 간섭이 줄어들어 수신거리도 길어지고 [안정적이다](https://www.zigbee2mqtt.io/how_tos/how_to_improve_network_range_and_stability.html).

* 홈어시스턴트에 센서 연동

1. 직비 usb 모듈이 정상적으로 라즈베리파이에 연결되어 홈어시스턴트에 잡힌다면, 왼쪽 HACS탭 -> 상단 System -> Host System에서 오른쪽 하단의 점3개 -> Hardware를 누르면 아래 화면과 같이 디바이스가 잡힌것이 보인다.(e.g. /dev/serial/by-id/usb-Texas_Instruments_TI_CC2531_USB_CDC___0X00124B0014D98CDD-if00)

![zigbee1](https://github.com/devtaste/home-assistant-tips/blob/master/images/zigbee1.jpg)

2. 왼쪽 Configuration 탭 -> User -> 오른쪽 하단 +ADD USER 버튼 을 눌러 새 user를 추가해준다. mqtt 라는 메세징 프로토콜을 사용하는 홈어시스턴트 Add-on(Zigbee2mqtt)을 사용하기때문에 user/password는 mqtt/mqtt 로 해주었다.

![zigbee2](https://github.com/devtaste/home-assistant-tips/blob/master/images/zigbee2.jpg)

3. 왼쪽 Supervisor 탭 -> 상단 Add-on Store 에서 mqtt검색 후 Mosquitto broker 선택하여 install

![zigbee3](https://github.com/devtaste/home-assistant-tips/blob/master/images/zigbee3.jpg)

4. Mosquitto broker Add-on에서 상단 Configuration 탭에서 아래와 같이 configuration 변경 후 Mosquitor broker start.

![zigbee4](https://github.com/devtaste/home-assistant-tips/blob/master/images/zigbee4.jpg)

5. 왼쪽 Configuration 탭 -> Integrations -> MQTT 에서 configure 버튼 클릭, 체크박스 선택 후 SEND 버튼 클릭

![zigbee5](https://github.com/devtaste/home-assistant-tips/blob/master/images/zigbee5.jpg)

6. 왼쪽 Supervisor 탭 -> 상단 Add-on Store -> 상단 오른쪽 점 3개 -> Repositories -> ***https://github.com/Koenkk/zigbee2mqtt*** 입력 후 ADD 버튼 클릭 -> 새로고침 하면 새롭게 zigbee2mqtt라는 Add-on 생김 -> INSTALL

![zigbee6](https://github.com/devtaste/home-assistant-tips/blob/master/images/zigbee6.jpg)

![zigbee7](https://github.com/devtaste/home-assistant-tips/blob/master/images/zigbee7.jpg)

7. zigbee2mqtt Add-on에서 상단 Configuration 아래와 같이 수정. (permit_join, server, user, password, port 부분) server에서 ip부분은 공유기 내부 네트워크에서 라즈베리파이(홈어시스턴트)가 잡고있는 IP. port는 1. 에서 확인했던 디바이스 경로 (e.g. /dev/serial/by-id/usb-Texas_Instruments_TI_CC2531_USB_CDC___0X00124B0014D98CDD-if00). SAVE 후 zigbee2mqtt start.

![zigbee8](https://github.com/devtaste/home-assistant-tips/blob/master/images/zigbee8.jpg)

### Acknowledgments
subscribers!!

