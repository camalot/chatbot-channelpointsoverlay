"use strict";
let animationEndClasses = "webkitAnimationEnd mozAnimationEnd MSAnimationEnd oanimationend animationend";
if (!window.settings) {
	window.settings = {};
}
window.settings = { ...DEFAULT_SETTINGS, ...window.settings };

function showRedemption(data) {
	if (!data || !data.displayName || !data.title || !data.image) {
		return;
	}
	$(":root").css("--bg-color", data.backgroundColor);
	$("#alert")
		.queue(function () {
			$("#name").html(data.displayName);
			$("#title").html(data.title);
			$("#prompt").html(data.prompt);
			$("#message").html(data.message);
			$("#pointsName").html(data.pointsName || "Points");
			$("#cost").html(data.cost);
			$("#message").html(data.message);
			$("#logo img").attr("src", data.image);

			// if (settings.InSound && settings.PlaySound) {
			// 	$("#sound embed").attr("src", settings.InSound);
			// }

			$("#alert")
				.removeClass()
				.addClass(`${settings.InTransition} animated`)
				.one(animationEndClasses, function () {
					console.log("end in transition")
					$(this)
						.off(animationEndClasses)
						.removeClass()
						.addClass(`${settings.InAttentionAnimation} animated`)
						.one(animationEndClasses, function () {
							$(this)
								.removeClass();
							console.log("end in attention animation");
						});
				})
				.dequeue();
		})
		.delay((settings.DisplaySeconds || 10) * 1000)
		.queue(function () {
			console.log("start out attention");
			// if (settings.OutSound && settings.PlaySound) {
			// 	$("#sound embed").attr("src", settings.OutSound);
			// }

			$("#alert")
				.removeClass()
				.off(animationEndClasses)
				.addClass(`${settings.OutAttentionAnimation} animated`)
				.one(animationEndClasses, function () {
					console.log("end out attention transition");
					$(this)
						.removeClass()
						.addClass(`${settings.OutTransition} animated`)
						.one(animationEndClasses, function () {
							console.log("end out transition")
							$(this)
								.removeClass().addClass("hidden");
						});
				})
				.dequeue();
		});
}

function initializeUI() {
	var fontName = settings.FontName;
	var customFontName = settings.CustomFontName;
	if (fontName && fontName === "custom" && customFontName && customFontName !== "") {
		loadFontsScript(customFontName);
	} else {
		$(":root").css("--font-name", fontName);
	}

	$(":root")
		.css("--font-name", `${settings.FontName}`)
		.css("--body-opacity", `${(settings.Opacity || 100) / 100}`)
		.css("--title-font-size", `${settings.TitleFontSize || 2}em`)
		.css("--name-font-size", `${settings.NameFontSize || 1.5}em`)
		.css("--message-font-size", `${settings.MessageFontSize || 1.5}em`)
		.css("--prompt-font-size", `${settings.PromptFontSize || 1.5}em`)
		.css("--name-color", `${settings.NameColor || "rgba(240, 240, 240, 1)"}`)
		.css("--name-stroke-width", `${settings.NameStrokeWidth || 0}px`)
		.css("--name-stroke-color", `${settings.NameStrokeColor || "rgba(0,0,0,0)"}`)
		.css("--title-color", `${settings.TitleColor || "rgba(240, 240, 240, 1)"}`)
		.css("--title-stroke-width", `${settings.TitleStrokeWidth || 0}px`)
		.css("--title-stroke-color", `${settings.TitleStrokeColor || "rgba(0,0,0,0)"}`)
		.css("--prompt-color", `${settings.PromptColor || "rgba(240, 240, 240, 1)"}`)
		.css("--prompt-stroke-width", `${settings.PromptStrokeWidth || 0}px`)
		.css("--prompt-stroke-color", `${settings.PromptStrokeColor || "rgba(0,0,0,0)"}`)
		.css("--message-color", `${settings.MessageColor || "rgba(240, 240, 240, 1)"}`)
		.css("--message-stroke-width", `${settings.MessageStrokeWidth || 0}px`)
		.css("--message-stroke-color", `${settings.MessageStrokeColor || "rgba(0,0,0,0)"}`)
		.css("--border-radius", `${settings.BorderRadius || "0"}%`)
		.css("--border-color", `${settings.BorderColor || "rgba(0,0,0,0)"}`)
		.css("--border-width", `${settings.BorderWidth || "0"}`)
		.css("--message-display", `${settings.ShowMessage ? "block" : "none"}`)
		.css("--prompt-display", `${settings.ShowPrompt ? "block" : "none"}`)
		;

	$("#logo img").removeClass().addClass(`${settings.ImageShape || "circle"}`);
}

function connectWebsocket() {
	//-------------------------------------------
	//  Create WebSocket
	//-------------------------------------------
	let socket = new WebSocket("ws://127.0.0.1:3337/streamlabs");
	//-------------------------------------------
	//  Websocket Event: OnOpen
	//-------------------------------------------
	socket.onopen = function () {
		// AnkhBot Authentication Information
		let auth = {
			author: "DarthMinos",
			website: "darthminos.tv",
			api_key: API_Key,
			events: [
				"EVENT_CHANNELPOINTS_SETTINGS",
				"EVENT_CHANNELPOINTS_REDEEMED"
			]
		};
		// Send authentication data to ChatBot ws server
		socket.send(JSON.stringify(auth));
	};

	//-------------------------------------------
	//  Websocket Event: OnMessage
	//-------------------------------------------
	socket.onmessage = function (message) {
		console.log(message);
		// Parse message
		let socketMessage = JSON.parse(message.data);
		let eventName = socketMessage.event;
		console.log(socketMessage);
		let eventData = typeof socketMessage.data === "string" ? JSON.parse(socketMessage.data || "{}") : socketMessage.data;
		switch (eventName) {
			case "EVENT_CHANNELPOINTS_REDEEMED":
				console.log(eventData);
				showRedemption(eventData);
				break;
			case "EVENT_CHANNELPOINTS_SETTINGS":
				window.settings = eventData;
				if (validateInit()) {
					initializeUI();
				}
				break;
			default:
				console.log(eventName);
				break;
		}
	};

	//-------------------------------------------
	//  Websocket Event: OnError
	//-------------------------------------------
	socket.onerror = function (error) {
		console.error(`Error: ${error}`);
	};

	//-------------------------------------------
	//  Websocket Event: OnClose
	//-------------------------------------------
	socket.onclose = function () {
		console.log("close");
		// Clear socket to avoid multiple ws objects and EventHandlings
		socket = null;
		// Try to reconnect every 5s
		setTimeout(function () { connectWebsocket(); }, 5000);
	};
}

function validateSettings() {
	let hasApiKey = typeof API_Key !== "undefined";
	let hasSettings = typeof settings !== "undefined";
	let hasOauth = settings.UserOAuth && settings.UserOAuth !== "";
	return {
		hasOauth: hasOauth,
		isValid: hasApiKey && hasSettings,
		hasSettings: hasSettings,
		hasApiKey: hasApiKey
	};
}

function validateInit() {
	// verify settings...
	let validatedSettings = validateSettings();
	// Connect if API_Key is inserted
	// Else show an error on the overlay
	if (!validatedSettings.isValid) {
		$("#config-messages").removeClass("hidden");
		$("#config-messages .settings").removeClass(validatedSettings.hasSettings ? "valid" : "hidden");
		$("#config-messages .api-key").removeClass(validatedSettings.hasApiKey ? "valid" : "hidden");
		$("#config-messages .oauth").removeClass(validatedSettings.hasOauth ? "valid" : "hidden");
		return false;
	}
	return true;
}

function loadFontsScript(font) {
	// bangers;amaranth;allan;bowlby-one;changa-one;days-one;droid-sans;fugaz-one;
	var script = document.createElement('script');
	script.onload = function () {
		$(":root").css("--font-name", font);
	};
	script.src = `http://use.edgefonts.net/${font}.js`;

	document.head.appendChild(script); //or something of the likes
}

jQuery(document).ready(function () {
	if (validateInit()) {
		initializeUI();
		connectWebsocket();
	} else {
		console.log("Invalid");
	}
});
