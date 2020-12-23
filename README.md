<div class="header" align="center">
	<h2>
		<a href="https://www.youtube.com/channel/UCpY10pb4-S0PwCJBp2r6nOvg" title="temp">
			<img alt="" src="https://yt3.ggpht.com/a/AATXAJyqMS98UZ8kCtNAyGD1NUPd4irEZQbl-SvW32JcgQ=s288-c-k-c0xffffffff-no-rj-mo" width="100px" height="100px" />
		</a>
		<br />
		Taste like Developer
	</h2>
	<p align="center">:octocat: home-assistant-tutorial</p>
</div>

---

### Overview
홈어시스턴트는 문서나 새로운 기능이 자주 바뀌고 업데이트가 되기 때문에, 블로그에 정리된 글을 보는것보단 공식 도큐먼트를 보는게 좋습니다. 이 문서는 홈 iot를 구축하면서 유튜브에서 다루거나 도움이 될만한 문서나 팁이 있으면 계속 업데이트 할 예정입니다. 댓글을 통해 자주 질문이 들어오는 내용이 있다면 여기에도 업데이트 하겠습니다.

Official document나 읽었던 자료중에 도움이 되었던 페이지 모음과 간략한 한글 팁& 설명

### Prerequisite
subscribe [Taste like Developer](https://www.youtube.com/channel/UCpY9pb4-S0PwCJBp2r6nOvg)

### Contributor(s)
- **Taste like Developer** - [Youtube](https://www.youtube.com/channel/UCpY9pb4-S0PwCJBp2r6nOvg)

### Contents
- 홈어시스턴트 설치: https://www.home-assistant.io/docs/installation/
    여러 설치 방법중, 라즈베리파이에 hassio(Home Assistant OS: 홈어시스턴트 전용 OS)방식으로 설치하는것이 공식 도큐먼트에서도 가장 추천하는 방식이다. 처음에 docker로 사용하다 이런저런 이유로 불편해서 바꿨음.

- YAML 파일: https://www.home-assistant.io/docs/configuration/yaml/
    .yaml은 .txt 같은 확장자일 뿐, 겁먹지 말자.

- 이케아 스마트 조명 예제: https://smartme.pl/home-assistant-integracja-z-systemem-ikea-tradfri/
    스마트조명이 가장 활용도가 좋고, 난이도도 쉽다.

- 샤오미 기기 연결: https://www.home-assistant.io/integrations/xiaomi_miio/
    샤오미부터는 난이도가 조금 올라간다. 샤오미 기기의 토큰을 추출해야하고, 기기의 ip 주소를 알아내야 한다, 토큰은 링크에서 보고 따라하면 되고, 연결된 ip주소는 미홈 앱에서 기기 설정 뒤져보면 나온다.

- 샤오미 로보락 청소기 연결 예제: https://psychoria.tistory.com/685
    공식 도큐먼트는 아닌데, 간결하게 정리를 잘 해두셨음.

- HACS: https://hacs.xyz/docs/basic/getting_started
    HACS는 커스텀 컴포넌트(고수들이 지원하지 않는 기기들을 컴포턴트로 만듬, e.g. 샤오미 선풍기)를 관리하는 도구이다.

- 샤오미 선풍기 커스텀 컴포넌트 깃헙: https://github.com/syssi/xiaomi_fan

- 구글어시선트 홈어시스턴트에 붙이기: https://www.home-assistant.io/integrations/google_assistant/
    홈어시스턴트에 붙인 기기들을 구글홈 스피커로 동작시키기 위함. hassio로 설치하지 않는다면 난이도 최상, hassio로 설치했다면 상. Home Assistant Cloud 는 유로이니 문서에서 Manual setup부터 보고 따라하면 된다. Warning 부분이 가장 중요해보임. 다행이 duckdns add-on이 알아서 ddns와 ssl인증 부분을 알아서 해주니 훨신 편해졌다. 공유기좀 만져봤거나 컴퓨터네트워크 수업때 안졸았으면 쉽게 할 수 있을것 같음.

- 자동화: https://www.home-assistant.io/blog/2020/07/22/release-113/

- 영상에서 사용한 자동화 스크립트 - 홈어시스턴트 앱이나 브라우저를 통해 gui로 작성 가능

```{.yaml}
- id: '1605805585154'
  alias: set purifier speed to 3 when vacuum start cleaning
  description: set purifier speed to 3 when vacuum start cleaning
  trigger:
  - platform: state
    entity_id: vacuum.smart_vacuum
    attribute: status
    to: Cleaning
  condition: []
  action:
  - service: fan.set_speed
    data:
      entity_id: fan.xiaomi_purifier
      speed: Fan
    entity_id: fan.xiaomi_purifier
  mode: single
- id: '1605845082998'
  alias: set purifier speed to auto when vacuum start charging
  description: set purifier speed to auto when vacuum start charging
  trigger:
  - platform: state
    entity_id: vacuum.smart_vacuum
    attribute: status
    to: Charging
  condition: []
  action:
  - service: fan.set_speed
    data:
      entity_id: fan.xiaomi_purifier
      speed: Auto
    entity_id: fan.xiaomi_purifier
  mode: single
- id: '1605874002653'
  alias: daily cleaning routine
  description: daily cleaning routine
  trigger:
  - platform: sun
    event: sunset
    offset: 05:50:00
  condition:
  - condition: and
    conditions:
    - condition: state
      entity_id: light.tradfri_driver
      state: 'off'
  action:
  - service: vacuum.start
    data: {}
    entity_id: vacuum.smart_vacuum
  mode: restart
```

- 영상에서 사용한 configuration.yaml

```{.yaml}
# Configure a default setup of Home Assistant (frontend, api, etc)
default_config:

lovelace:
  mode: yaml

# Text to speech
tts:
  - platform: google_translate

group: !include groups.yaml
automation: !include automations.yaml
script: !include scripts.yaml
scene: !include scenes.yaml

# Example configuration.yaml entry
sensor:
  - platform: command_line
    name: CPU Temperature
    command: "cat /sys/class/thermal/thermal_zone0/temp"
    # If errors occur, make sure configuration file is encoded as UTF-8
    unit_of_measurement: "°C"
    value_template: '{{ value | multiply(0.001) | round(1) }}'

vacuum:
  - platform: xiaomi_miio
    name: Smart Vacuum
    host: 192.168.0.5
    token: abcdabcdabcdabcdabcdabcdabcdabccd

fan:
  #- platform: xiaomi_miio_fan
  #  name: Smart Fan
  #  host: 192.168.0.9
  #  token: abcdabcdabcdabcdabcdabcdabcdabccd

  - platform: xiaomi_miio
    name: Smart Purifier
    host: 192.168.0.8
    token: abcdabcdabcdabcdabcdabcdabcdabccd

google_assistant:
  project_id: ha-docker
  service_account: !include SERVICE_ACCOUNT.JSON

http:
  ssl_certificate: /ssl/fullchain.pem
  ssl_key: /ssl/privkey.pem
```

### Acknowledgments
subscribers!!
