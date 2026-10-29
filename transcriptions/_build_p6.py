# -*- coding: utf-8 -*-
"""Sentence-level Hindi and English for Damodar Lila part 6."""

import json
from pathlib import Path

from lectures.timeline import cues_to_srt

ROOT = Path("work/damodar-lila/2012-10-28")

# Inclusive cue numbers from the timed Hindi pass.
GROUPS = [
(
"ॐ नमो भगवते वासुदेवाय।",
"Om namo bhagavate vasudevaya.",
),
(
"वाणी गुणानुकथने श्रवणौ कथायां हस्तौ च कर्मसु मनस्तव पादयोर्नः। स्मृत्यां शिरस्तव निवासजगत्प्रणामे दृष्टिः सतां दर्शनेऽस्तु भवत्तनूनाम्। [श्रीमद्भागवतम् 10.10.38]",
"May our words describe Your pastimes, our ears hear Your glories, our hands work for You, and our mind remember Your lotus feet. May our head bow to the whole world, because You live in it, and may our eyes see the Vaishnavas, who are nondifferent from You. [Srimad-Bhagavatam 10.10.38]",
),
(
"नलकूवर और मणिग्रीव भगवान कृष्ण की स्तुति कर रहे हैं। स्तुति करते हुए उनके मन में आया कि यहाँ रहना ठीक नहीं। भगवान ऊखल में बंधे हैं, और माता यशोदा घर के कामों में व्यस्त हैं। देवता के रूप में दो देवताओं का रहना भगवान की लीला में विघ्न डालेगा। माता गोद में नहीं ले पाएँगी, बच्चे खेल नहीं पाएँगे। हम कुबेर के पुत्र हैं, सौ दिव्य वर्षों तक वृक्ष रहे, और अब कृपा से मुक्त हुए हैं। लीला में बाधक नहीं बनना चाहिए।",
"Nalakuvara and Manigriva are praising Lord Krishna. While praising Him, they feel they should not stay. The Lord is tied to the mortar, and Mother Yashoda is busy with the housework. If two demigods remain in their demigod forms, they will disturb the pastime. Mother will not be able to take Him on her lap, and the children will not be able to play. They are Kuvera's sons. They were trees for a hundred years of the demigods, and now they are free by His mercy. They must not become an obstacle in the pastime.",
),
(
"इसलिए वे जाने की अनुमति माँग रहे हैं। अनुजानीहि, हमें आज्ञा दीजिए।",
"So they ask permission to leave. Anujanihi: please give us the order.",
),
(
"स्तुति के अंत में वे कहते हैं, अनुजानीहि नौ भूमन्। हे भूमन, आप सबके हृदय में हैं, सर्वव्यापी हैं। हमारी इच्छा आप जानते ही हैं। हम ब्रह्ज में, महावन में, आपकी लीला देखना चाहते हैं। पर हम देवता हैं। शरीर, तेज, सब भिन्न है। यहाँ रहने से और विघ्न होगा। आज्ञा दीजिए, हम अलकापुरी, पिता के घर, जाना चाहते हैं। [श्रीमद्भागवतम् 10.10.37]",
"At the end of the prayer they say, anujanihi nau bhuman. O Lord, You are in every heart. You are all-pervading. You already know our wish. We want to stay in Braj and see Your pastimes in Mahavana. But we are demigods. Our bodies and our splendor are different. If we stay, there will only be more disturbance. Please permit us. We want to go to Alakapuri, our father's house. [Srimad-Bhagavatam 10.10.37]",
),
(
"भगवान की लीला में परिकर गोपबालक रह सकते हैं। देवता बेढंगे लगते हैं। बच्चा खुलकर लीला नहीं कर पाएगा। यदि देवता सबके सामने इस नन्हे बालक को प्रणाम करने लगें, तो माता यशोदा के वात्सल्य में अंतर आ जाएगा। वह सोचेगी, यह हमारा बच्चा भगवान है। प्रेम शिथिल हो जाएगा। यही बात गोपबालकों के साथ भी है।",
"In the Lord's pastimes, the associates are the cowherd boys. A demigod looks out of place. The child will not be free to play. If demigods start bowing to this tiny child in front of everyone, Mother Yashoda's vatsalya, her love as a mother, will be disturbed. She will think, this child of mine is the Lord. The love will grow weak. The same will happen with the cowherd boys.",
),
(
"इसीलिए नलकूवर और मणिग्रीव सोच रहे हैं कि महावन से चल देना चाहिए। हे भूमन, आप हृदय जानते हैं। चाहकर भी हम यहाँ नहीं रह पाएँगे। जाने की आज्ञा दीजिए।",
"So Nalakuvara and Manigriva think they should leave Mahavana. O Lord, You know our hearts. Even though we want to stay, we cannot. Please permit us to go.",
),
(
"हमें जानिए, हम तवानुचर-किङ्करौ हैं। आपके अनुचर श्री नारद मुनि के दास हैं। अथवा आपके अनुचर महादेव के, या कुबेर के। पर यहाँ स्पष्ट अर्थ यही है कि हम नारद मुनि के किंकर हैं। [श्रीमद्भागवतम् 10.10.37]",
"Please know us as tavanucara-kinkarau, servants of Your servant. We are servants of Your servant Narada Muni. The words can also point to Mahadeva, or to Kuvera. But the clear meaning here is that we are Narada Muni's kinkaras. [Srimad-Bhagavatam 10.10.37]",
),
(
"किंकर उसे कहते हैं जो सदा तत्पर रहे, किं करोमि, मैं क्या करूँ। स्वामी को बुलाना नहीं पड़ता। मैं नारद मुनि का किंकर हूँ। आज्ञा दीजिए, हम अलकापुरी जा रहे हैं।",
"A kinkara is a servant who is always ready, thinking, kim karomi, what shall I do? The master does not even have to call him. I am Narada Muni's kinkara. Please give the order. We are going to Alakapuri.",
),
(
"दर्शनं नौ भगवत ऋषेर आसीद् अनुग्रहात्। आपका दर्शन नारद मुनि की कृपा से मिला। हमारी योग्यता नहीं थी। हम मदिरा पीकर स्त्रियों के साथ विहार कर रहे थे। नरक के योग्य थे। नारद जी ने आपके दर्शन की व्यवस्था कर दी। [श्रीमद्भागवतम् 10.10.37]",
"Darshanam nau bhagavata risher asid anugrahat. We have seen You by the mercy of the sage Narada. We had no qualification. We were drinking and sporting with women. We were fit for hell. Narada arranged for us to see You. [Srimad-Bhagavatam 10.10.37]",
),
(
"हम अपने घर जा रहे हैं। पर हे प्रभो, अलकापुरी में विषय-भोग का डर है। इंद्रियाँ विषय की ओर हैं। इसलिए एक प्रार्थना है।",
"We are going home. But, O Lord, in Alakapuri there is the danger of sense enjoyment. Our senses already run toward their objects. So we have one prayer.",
),
(
"वाणी गुणानुकथने श्रवणौ कथायाम्। जहाँ भी रहें, वाणी आपके गुण गाने में लगी रहे। गुण का अर्थ गुण है, सत्त्व, रज, तम भी है, और रस्सी भी। उसी रस्सी ने हमारा उद्धार किया। आपके उदर में रस्सी बंधी थी, इसी चर्चा को हम स्वर्ग में भी करते रहें। माधुर्य, कृपा, सौंदर्य, कोई दूसरा शब्द जिह्वा पर न आए। [श्रीमद्भागवतम् 10.10.38]",
"Vani gunanukathane shravanau kathayam. Wherever we live, let our words stay busy singing Your qualities. Guna means Your qualities. It also means the three modes, sattva, rajas, and tamas. And guna means a rope. That rope delivered us. A rope was tied around Your belly. Let us keep telling that, even in heaven. Your sweetness, Your mercy, Your beauty. Let no other word come on the tongue. [Srimad-Bhagavatam 10.10.38]",
),
(
"अनुकथन का अर्थ है लगातार कहना, टालना नहीं। अनंत लीला, अनंत कथा, अनंत गुण। यदि मनुष्य भगवान के गुण बोलता रहे, तो माया पकड़ नहीं सकती। कीर्तनीयः सदा हरिः। यही दोनों भाई माँग रहे हैं। [शिक्षाष्टक]",
"Anukathana means to keep speaking, not to postpone it. The pastimes, the katha, and the qualities have no end. If a person keeps speaking the Lord's qualities, maya cannot catch him. Kirtaniyah sada harih, Hari is always to be chanted. This is what the two brothers are asking. [Sikshashtaka]",
),
(
"हमारी वाणी आपके गुण-कथन में, दोनों कान आपकी कथा में, दोनों हाथ आपकी सेवा में लगे रहें। मन आपके चरणकमलों की स्मृति में, और श्रीविग्रह के चिंतन में लगा रहे।",
"Let our speech stay in Your glorification, both ears in Your katha, and both hands in Your service. Let the mind stay in remembrance of Your lotus feet, and in meditation on Your deity.",
),
(
"सिर सदा प्रणाम में झुका रहे। आप समस्त जगत में निवास करते हैं। जिस वस्तु को देखें, जिस जीव को देखें, यह भाव रहे कि आप उसमें हैं, और मस्तक झुक जाए। अहंकार और प्रमाद न हो। जिसे देखें, उसमें आपको देखकर प्रणाम करते रहें।",
"Let the head always stay bowed in pranam. You live in the whole world. Whatever object we see, whatever living being, let us feel that You are there, and let the head bow. No pride, and no carelessness. Whomever we see, let us see You there and offer pranam.",
),
(
"दृष्टिः सतां दर्शनेऽस्तु। आँखें आपके भक्तों का, वैष्णवों का दर्शन करती रहें। भवत्तनूनाम्, वे आपके ही शरीर हैं। आपमें और भक्त में भेद नहीं है।",
"Drishtih satam darshane astu. Let our eyes stay on Your devotees, the Vaishnavas. Bhavat-tanunam: they are Your own body. There is no difference between You and Your devotee.",
),
(
"वाणी, कान और हाथ की यह माँग गीता में भगवान ने बहुत जोर से कही है। मेरे लिए कर्म करो। नलकूवर और मणिग्रीव अलकापुरी में भी आपकी सेवा करना चाहते हैं। ग्यारहवें अध्याय में, मत्कर्मकृत् मत्परमो मद्भक्तः सङ्गवर्जितः। जो मेरे लिए कर्म करे, मुझे ही परम माने, मेरा भक्त हो, आसक्ति से रहित हो, निर्मम और निरहंकार हो, वह मुझे प्राप्त होता है। [भगवद्गीता 11.55]",
"The Lord has stressed this speech, these ears, and these hands in the Gita. Work for Me. Nalakuvara and Manigriva want to serve Him even in Alakapuri. In the eleventh chapter: mat-karma-krit mat-paramo mad-bhaktah sanga-varjitah. One who works for Me, who holds Me as supreme, who is My devotee, who is free from attachment, without possessiveness and without false ego, attains Me. [Bhagavad-gita 11.55]",
),
(
"कभी काम करके पीछे से अर्पण कर देते हैं। भोजन बनाकर फिर भगवान को चढ़ा देते हैं। वह भी भक्ति है। पर आरंभ से ही भगवान के लिए पकाना, अपने लिए नहीं, यही भाव सर्वश्रेष्ठ है। अर्पण अलग बात है, और भगवान के लिए ही काम करना अलग बात है।",
"Sometimes we work and offer the result afterward. We cook, and then we offer the food to the Lord. That is also devotion. But to cook for the Lord from the start, and not for ourselves, that feeling is the best. Offering the finished work is one thing. Working for the Lord from the beginning is another.",
),
(
"हाथ आपकी सेवा में लगें। आरती, श्रृंगार, मंदिर की सफाई, फुलवाड़ी सींचना, यह परिचर्या है। श्रील प्रभुपाद कहते हैं, इसे उपलक्षण मानो। हाथ, पैर, सारी इंद्रियाँ आपकी सेवा में लगें। पैर मंदिर जाएँ, धाम की परिक्रमा करें। जब इंद्रियाँ ऐसे लग जाएँ, तब अलकापुरी हमारा कुछ नहीं बिगाड़ सकती।",
"Let the hands stay in Your service. Arati, dressing the Lord, cleaning the temple, watering His garden. That is paricharya. Srila Prabhupada says to take this as a wider hint. Let the hands, the feet, and all the senses stay in Your service. Let the feet go to the temple and walk in parikrama of the dhama. When the senses are fixed like this, Alakapuri cannot harm us.",
),
(
"हर भक्त को यही प्रार्थना करनी चाहिए। कर्म के अनुसार जहाँ रहना हो, रहें। पर वाणी कीर्तन में, मन स्मरण में, हाथ सेवा में, कान कथा में लगे रहें। तब कहीं भी रहना ठीक है। मन यदि मुझमें लगा है, तो वह मुझे से खोता नहीं।",
"Every devotee should pray like this. Live wherever your karma places you. But let speech stay in kirtan, the mind in remembrance, the hands in service, and the ears in katha. Then any place is fine. If the mind is fixed on Me, that devotee is never lost to Me.",
),
(
"जो मुझे सब वस्तुओं में, सब जगह देखता है, और सब वस्तुओं को मुझमें देखता है, मैं उसे ओझल नहीं होता, और वह मुझे से दूर नहीं होता। [भगवद्गीता 6.30]",
"One who sees Me in everything, everywhere, and sees everything in Me, is never lost to Me, and I am never lost to him. [Bhagavad-gita 6.30]",
),
(
"नलकूवर यही माँग रहे हैं। जिस वस्तु या व्यक्ति को देखें, तुरंत स्मरण हो कि कृष्ण इस रूप में हैं, और मस्तक झुक जाए। तब अपराध नहीं होता। अपराध तब होता है जब हम अपने में बड़प्पन मानते हैं, क्योंकि भगवान सब जगह दिखते नहीं।",
"This is what Nalakuvara is asking. Whatever thing or person we see, let us at once remember that Krishna is present in that form, and let the head bow. Then offense does not come. Offense comes when we feel we are greater, and that happens because we cannot see the Lord everywhere.",
),
(
"ग्यारहवें स्कंध में हरि-योगेश्वर कहते हैं, खं वायुमग्निं सलिलं महीं च ज्योतींषि सत्त्वानि दिशो द्रुमादीन्। सरित्समुद्रांश्च हरेः शरीरं यत्किञ्च भूतं प्रणमेदनन्यः। आकाश, वायु, अग्नि, जल, पृथ्वी, सूर्य, चंद्र, तारे, वृक्ष, पशु, पक्षी, जो कुछ भी है, वह हरि का शरीर है। इस बुद्धि से सबको प्रणाम करे। [श्रीमद्भागवतम् 11.2.41]",
"In the Eleventh Canto the Hari-yogeshvaras say: kham vayum agnim salilam mahim ca, jyotimshi sattvani disho drumadin, sarit-samudrams ca hareh sariram, yat kim ca bhutam pranamed ananyah. Sky, air, fire, water, earth, the sun, the moon, the stars, the trees, the animals, the birds, whatever exists, is the body of Hari. With that understanding, offer pranam to all. [Srimad-Bhagavatam 11.2.41]",
),
(
"निवास-जगत्-प्रणामे। आप समस्त जगत में रहते हैं, यह देखकर सबको प्रणाम करना भगवान को ही प्रणाम है। जड़ में भी हैं, चेतन में तो कहना ही क्या। सब भगवान नहीं हैं, पर सबमें भगवान हैं। ऐसा प्रणाम भक्ति की बहुत ऊँची स्थिति है।",
"Nivasa-jagat-praname. You live in the whole world, and pranam offered with that vision is pranam to the Lord. He is in dull matter too, what to speak of living beings. Everything is not the Lord, but the Lord is in everything. Pranam of this kind is a very high stage of devotion.",
),
(
"प्रह्लाद महाराज ने कहा, एतावानेव लोकेऽस्मिन् पुंसः स्वार्थः परः स्मृतः। एकान्तभक्तिर्गोविन्दे यत्सर्वत्र तदीक्षणम्। भगवान को सब जगह देखना ही जीव का सबसे बड़ा पुरुषार्थ है। तब किसी का तिरस्कार नहीं होता, निंदा नहीं होती। निज प्रभु सब जगह हैं, तो किससे वैर करें? विरोध किया तो कृष्ण से विरोध हुआ। सबसे प्रेम होगा। [श्रीमद्भागवतम् 7.7.55]",
"Prahlada Maharaja said, etavan eva loke 'smin pumsah svarthah parah smritah, ekanta-bhaktir govinde yat sarvatra tad-ikshanam. To see the Lord everywhere is the living being's greatest gain. Then no one is looked down on, and no one is criticized. Our own Lord is everywhere, so with whom will we fight? To oppose someone is to oppose Krishna. There will be love for all. [Srimad-Bhagavatam 7.7.55]",
),
(
"इसी भाव से हमें विदा कीजिए। इंद्रियाँ आपमें अनुरक्त रहें, तो कहीं जाना हानि नहीं। अलकापुरी में वे सुनाएँगे, भगवान ने माखन चुराया, माता यशोदा ने ऊखल से बाँधा, और दामोदर ने उसी ऊखल से हमारा उद्धार किया। अपने गाँव और देश में जाकर यही कृष्ण-भावनामृत बाँटना चाहिए, जैसे नलकूवर और मणिग्रीव पिता की राजधानी में ये कथाएँ कहते रहे। छहों इंद्रियाँ भगवान में लग जाएँ, यही कृष्णभावनामृत है, दिव्य स्थिति है। उस भक्त का सब जगह मंगल ही मंगल है।",
"With this feeling, please bid us farewell. If the senses stay attached to You, there is no harm in going anywhere. In Alakapuri they will tell how the Lord stole the butter, how Mother Yashoda tied Him to the mortar, and how Damodara delivered them by that mortar. A person should go to his own town and country and share this Krishna consciousness, as Nalakuvara and Manigriva kept telling these kathas in their father's capital. When the senses stay fixed on the Lord, that is Krishna consciousness. That is the divine position. For that devotee, every place is auspicious.",
),
(
"इत्थं सङ्कीर्तितस्ताभ्यां भगवान् गोकुलेश्वरः दाम्ना चोलूखले बद्धः प्रहसन्नाह गुह्यकौ। बड़ी स्तुति सुनकर ऊखल में बंधे दामोदर मुसकराने लगे। हँसी इसलिए कि सामान्य नियम में मैं मुक्त रहता हूँ और बद्ध जीव मुक्ति के लिए स्तुति करते हैं। यहाँ उलटा हो गया। मैं बद्ध हूँ, और मुक्त जीव मेरी स्तुति कर रहे हैं। बालकृष्ण हँसते हुए बोल रहे हैं। [श्रीमद्भागवतम् 10.10.39]",
"Ittham sankirtitas tabhyam bhagavan gokulesvarah, damna colukhale baddhah prahasann aha guhyakau. After this great prayer, Damodara, tied to the mortar, began to smile. The smile is because the ordinary rule is that He stays free, and the bound souls pray to be freed. Here it is reversed. He is bound, and the freed souls are praising Him. Child Krishna is speaking, and smiling. [Srimad-Bhagavatam 10.10.39]",
),
(
"ज्ञातं मम पुरैवैतत्। ये बातें मुझे पहले से मालूम हैं, कम से कम सौ दिव्य वर्ष पहले से। नारद ने जो किया, वह मैं ही जानता हूँ, मैं ही किया हूँ। छोटे बालक की तुतली बोली में कह रहे हैं, और बंधन का खेद नहीं, आनंद है। [श्रीमद्भागवतम् 10.10.40]",
"Jnatam mama puraivaitat. I have known all this from before, at least from a hundred years of the demigods ago. What Narada did, I knew, and I Myself did it. He is saying it in the lisping voice of a small child, and He is not sorry to be bound. He is joyful. [Srimad-Bhagavatam 10.10.40]",
),
(
"ऋषिणा करुणात्मना। नारद के हृदय में करुणा बसी है। तुम श्रीमद से अंधे थे, मदिरा और विषय में थे। वाग्भिः, केवल वचन से, उन्होंने विभ्रंश किया। कर्म के अनुसार महाघोर नरक था, कैलास पर गंगा के पास भी यह पाप नरक ले जाता। नारद की दृष्टि पड़ी, और उन्होंने ब्रज में जन्म और मेरा दर्शन दे दिया। सबसे बड़ा अनुग्रह यही है। भगवान भक्त का श्रेय भक्त को ही देते हैं। तुम्हें दर्शन नारद की कृपा से मिला। [श्रीमद्भागवतम् 10.10.40]",
"Rishina karunatmana. Compassion lives in Narada's heart. You were blind with wealth, lost in wine and sense pleasure. Vagbhih, by his words alone, he brought you down. By your karma a terrible hell was waiting. Even on Kailasa, beside the Ganga, that act leads to hell. Narada's glance fell on you, and he gave you birth in Braj and My darshan. That is the greatest mercy. The Lord gives the credit to His devotee. Your darshan came by Narada's mercy. [Srimad-Bhagavatam 10.10.40]",
),
(
"साधूनां समचित्तानां सुतरां मत्कृतात्मनाम्। दर्शनान्नो भवेद बन्धः पुंसोऽक्ष्णोः सवितुर्यथा। मेरे भक्त समदर्शी हैं, मन सदा मुझमें लगा है। उनके दर्शन से अज्ञान वैसे ही मिटता है जैसे सूर्य के सामने आँख का अंधकार। जीवन में सद्गुण उगते हैं, और मुझसे मिलने का सुयोग मिलता है। [श्रीमद्भागवतम् 10.10.41]",
"Sadhunam sama-cittanam sutaram mat-kritatmanam, darshanan no bhaved bandhah pumso 'kshnoh savitur yatha. My devotees are equal to all, and their minds stay fixed on Me. By seeing them, ignorance leaves, as darkness leaves the eyes when they face the sun. Good qualities grow, and the chance comes to meet Me. [Srimad-Bhagavatam 10.10.41]",
),
(
"भगवान का स्वभाव है कि भक्त की प्रशंसा करते हैं। भक्त कहते हैं, सब आपकी कृपा है। भगवान कहते हैं, तुम्हारे परिश्रम से हुआ। यहाँ भगवान कह रहे हैं, दुर्गति से बचना, मेरे धाम में कुछ वर्ष रहना, और मेरा दर्शन, सब नारद मुनि की कृपा है।",
"It is the Lord's nature to praise the devotee. The devotee says, it is all Your mercy. The Lord says, it came by your effort. Here the Lord says, you were saved from a bad end, you lived some years in My dhama, and you saw Me, all by Narada Muni's mercy.",
),
(
"तद् गच्छतं मत्परमौ नलकूवर सादनम्। सञ्जातो मयि भावो वामीप्सितः परमोऽभवः। हे नलकूवर, दोनों महाभाग्यशाली हो। घर जाओ। तुममें मेरे प्रति परम भाव, श्रेष्ठ प्रेम, उत्पन्न हो गया है। अब जन्म-मृत्यु का बंधन समाप्त है। [श्रीमद्भागवतम् 10.10.42]",
"Tad gacchatam mat-paramau nalakuvara sadanam. Sanjato mayi bhavo vam ipsitah paramo 'bhavah. O Nalakuvara, both of you are greatly fortunate. Go home. The highest bhava, the finest love for Me, has awakened in you. The bondage of birth and death is finished. [Srimad-Bhagavatam 10.10.42]",
),
(
"दोनों भाई ऊखल में बंधे भगवान को प्रणाम करने लगे। दाम्ना बद्धः, रस्सी से बंधे थे, और वास्तव में यशोदा और नंद के प्रेम में बंधे थे। बंधे-बंधे ही बात कर रहे थे।",
"The two brothers began to offer pranam to the Lord, who was tied to the mortar. Damna baddhah, He was tied with the rope, and in truth He was tied by the love of Yashoda and Nanda. He was speaking while bound.",
),
(
"इत्युक्दौ तौ परिक्रम्य प्रणम्य च पुनः पुनः। कृष्ण की परिक्रमा की, और ऊखल की भी, क्योंकि भगवान ऊखल में बंधे थे। [श्रीमद्भागवतम् 10.10.43]",
"Ity uktau tau parikramya pranamya ca punah punah. They circumambulated Krishna, and the mortar as well, because the Lord was tied to it. [Srimad-Bhagavatam 10.10.43]",
),
(
"उन्होंने कहा, प्रभो, हमें और कुछ नहीं चाहिए। पिता राजाओं के राजा हैं, धन की कमी नहीं, यक्ष और देव कन्याएँ पत्नियाँ हैं, रूप कामदेव के समान है, शरीर युवा है, स्वर्ग के भोग हैं।",
"They said, O Lord, we need nothing else. Our father is the king of kings. There is no lack of wealth. Yaksha and deva daughters are our wives. Our beauty is like Kamadeva's. The body is young. The enjoyments of heaven are there.",
),
(
"यान पुष्पक है, मन की गति से चलता है, जितने लोग हों उतना फैलता है। जब राम लंका से अयोध्या जाने लगे, और भरत की चिंता हुई, तब विभीषण ने पुष्पक दिया, जो रावण ने कुबेर से छीना था। सब वानर उस पर चढ़े। नलकूवर और मणिग्रीव कहते हैं, हमारे पास भी वही पुष्पक है, और निवास अलकापुरी है। पेट्रोल नहीं लगता। मन जहाँ संकल्प करे, वहीं उतरता है।",
"The vehicle is Pushpaka. It moves at the speed of the mind, and it expands to hold as many as must ride. When Rama was leaving Lanka for Ayodhya, anxious that Bharata might not live if He were late, Vibhishana gave Him Pushpaka, which Ravana had taken from Kuvera. All the vanaras boarded it. Nalakuvara and Manigriva say, we also have that Pushpaka, and our home is Alakapuri. It needs no fuel. It lands wherever the mind intends.",
),
(
"नगर अमरावती के समान धनी है। कमी कुछ नहीं। भगवान कहें भी कि माँगो, तो वे कहते हैं, हमारे लिए प्रार्थना केवल एक है। यह सुंदर कृष्णनाम कभी न भूले। नाम जिह्वा पर रहे, रूप मन में रहे।",
"The city is as rich as Amaravati. Nothing is lacking. Even if the Lord says, ask, they say, we have only one prayer. May this beautiful name of Krishna never be forgotten. Let the name stay on the tongue, and the form stay in the mind.",
),
(
"वे ऊखल में बंधे भगवान को, ऊखल को, और रस्सी को बार-बार प्रणाम कर रहे हैं। मंगलकामना कर रहे हैं, तुम कृष्ण के साथ बंधे रहो। तुम्हारे इस उपकार को हम नहीं भूलेंगे। यदि ऊखल उदर से न बंधा होता, तो हम अब तक वृक्ष खड़े रहते।",
"Again and again they offer pranam to the Lord tied to the mortar, to the mortar, and to the rope. They bless it: stay tied to Krishna. We will never forget this favor. If the mortar had not been tied to His belly, we would still be standing as trees.",
),
(
"नमस्तेऽस्तु दाम्ने स्फुरद्दीप्तिधाम्ने त्वदीयोदरायाथ विश्वस्य धाम्ने। रस्सी को प्रणाम, जिससे दीप्ति फूटती है। उदर को प्रणाम, जो विश्व का धाम है। खींचते समय जोर पेट पर पड़ा, इसलिए उदर ने भी उद्धार किया। स्वार्थ से नहीं, प्रेम से प्रणाम है। यह दामोदराष्टक में है। [पद्मपुराण, दामोदराष्टक]",
"Namas te 'stu damne sphurad-dipti-dhamne, tvadiyodarayatha visvasya dhamne. Pranam to the rope, from which light bursts forth. Pranam to the belly, which is the home of the universe. When He pulled, the force came on the belly, so the belly also delivered them. This pranam is from love, not from selfishness. This is in the Damodarashtakam. [Padma Purana, Damodarashtakam]",
),
(
"ऐसा प्रणाम कुंती ने भी किया। नमः पङ्कजनाभाय नमः पङ्कजमालिने। नमः पङ्कजनेत्राय नमस्ते पङ्कजाङ्घ्रये। भतीजा है, संकोच होता, इसलिए नाभि से प्रणाम आरंभ किया, फिर नेत्र, फिर चरण। नलकूवर भी उसी तरह कर रहे हैं। [श्रीमद्भागवतम् 1.8.22]",
"Kunti offered pranam in this same way. Namah pankaja-nabhaya, namah pankaja-maline, namah pankaja-netraya, namas te pankajanghraye. He is her nephew, so there is shyness. She began from the lotus navel, then the eyes, then the feet. Nalakuvara is doing the same. [Srimad-Bhagavatam 1.8.22]",
),
(
"नमो राधिकायै त्वदीयप्रियायै। श्रीमति राधारानी को प्रणाम। नमोऽनन्तलिलाय देवाय तुभ्यम्। अनंत लीला करने वाले आपको प्रणाम। ऊखल, रस्सी, और भगवान को पुनः पुनः परिक्रमा और प्रणाम। [दामोदराष्टक]",
"Namo radhikayai tvadiya-priyayai. Pranam to Your beloved, Srimati Radharani. Namo 'nanta-lilaya devaya tubhyam. Pranam to You, who perform endless pastimes. Again and again, parikrama and pranam to the mortar, the rope, and the Lord. [Damodarashtakam]",
),
(
"फिर आज्ञा लेकर उत्तर दिशा चले, अलकापुरी हिमालय की ओर है। उत्तर में महात्मा और वैष्णव रहते हैं, बदरिकाश्रम है, जहाँ नारद सबसे अधिक रहते हैं। पहले नारद को कृतज्ञता ज्ञापन और प्रणाम, फिर कैलास पर शिव जी के दर्शन। [श्रीमद्भागवतम् 10.10.43]",
"Then, taking permission, they left toward the north. Alakapuri is toward the Himalaya. In the north live the great souls and the Vaishnavas, and Badrikashram, where Narada stays most of all. First they will thank Narada and offer him pranam, and then at Kailasa they will see Lord Shiva. [Srimad-Bhagavatam 10.10.43]",
),
(
"ऊखल से कह रहे थे, तुम्हारा उपकार हम नहीं भूलेंगे। यदि यह उदर से न बंधा होता, तो दोनों वृक्ष अब तक खड़े रहते। ऊखल अटका, और वृक्ष उखड़ गए। इस तरह दामोदर ने नलकूवर और मणिग्रीव को मुक्त किया, और परम भाव दिया। परम प्रेम मिलने पर पार्षदत्व मिलता है, और नित्य ब्रजलीला में प्रवेश। हरे कृष्ण। जय श्रील प्रभुपाद।",
"They were telling the mortar, we will never forget your favor. If you had not been tied to this belly, the two trees would still be standing. The mortar caught, and the trees were uprooted. In this way Damodara freed Nalakuvara and Manigriva and gave them the highest love. When that prema comes, one can become the Lord's associate and enter the eternal pastimes of Braj. Hare Krishna. Jaya Srila Prabhupada.",
),
]

RANGES = [
(1, 1), (2, 6), (7, 16), (17, 18), (19, 26), (27, 35), (36, 42), (43, 51),
(52, 61), (62, 71), (72, 75), (76, 92), (93, 98), (99, 115), (116, 130),
(131, 136), (137, 154), (155, 162), (163, 175), (176, 183), (184, 187),
(188, 194), (195, 212), (213, 220), (221, 233), (234, 250), (251, 266),
(267, 283), (284, 312), (313, 330), (331, 338), (339, 361), (362, 369),
(370, 373), (374, 383), (384, 404), (405, 415), (416, 430), (431, 436),
(437, 444), (445, 449), (450, 460), (461, 471),
]


def main() -> None:
    if len(GROUPS) != len(RANGES):
        raise SystemExit(f"groups {len(GROUPS)} ranges {len(RANGES)}")
    expected = 1
    for start, end in RANGES:
        if start != expected:
            raise SystemExit(f"gap before {start}, expected {expected}")
        expected = end + 1
    if expected != 472:
        raise SystemExit(f"ended at {expected - 1}")
    raw = json.loads((ROOT / "cues.json").read_text(encoding="utf-8"))
    cues = []
    blocks = []
    for (start, end), (hindi, english) in zip(RANGES, GROUPS):
        cue = {
            "start": raw[start - 1]["start"],
            "end": raw[end - 1]["end"],
            "text": hindi,
            "english": english,
        }
        cues.append(cue)
        blocks.append(hindi.strip())
        blocks.append(english.strip())
        blocks.append("")
    (ROOT / "cues_polished.json").write_text(
        json.dumps(cues, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (ROOT / "hindi.srt").write_text(cues_to_srt(cues, "text"), encoding="utf-8")
    (ROOT / "english.srt").write_text(cues_to_srt(cues, "english"), encoding="utf-8")
    (ROOT / "bilingual.txt").write_text("\n".join(blocks), encoding="utf-8")
    meta = json.loads((ROOT / "meta.json").read_text(encoding="utf-8"))
    meta["english"] = "simple English, sentence by sentence, after the whole katha"
    meta["hindi"] = "standard Hindi spelling; Bihari ya/ja and va/ba corrected"
    meta["polished_cues"] = len(cues)
    meta["scripture"] = (
        "Quoted verses were taken from Srimad-Bhagavatam 10.10.37-43, 11.2.41, "
        "7.7.55, and 1.8.22, Bhagavad-gita 11.55 and 6.30, the Sikshashtaka, "
        "and the Damodarashtakam."
    )
    (ROOT / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print("cues", len(cues), "last", cues[-1]["end"])


if __name__ == "__main__":
    main()
