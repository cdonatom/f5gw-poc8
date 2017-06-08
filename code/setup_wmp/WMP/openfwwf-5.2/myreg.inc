/* Registers definition */


#define		GLOBAL_FLAGS_REG1		r0
#define 	GLOBAL_FLAGS_REG2		r45
#define 	GLOBAL_FLAGS_REG3		r2
#define 	TX_TYPE_SUBTYPE			r3
#define 	RX_TYPE				r4
#define 	RX_TYPE_SUBTYPE			r5
#define 	MIN_CONTENTION_WIN		r6
#define 	MAX_CONTENTION_WIN		r7
#define 	CUR_CONTENTION_WIN		r8
#define 	RX_TIME_WORD3			r9
#define 	RX_TIME_WORD2			r10
#define 	RX_TIME_WORD1			r11
#define 	RX_TIME_WORD0			r12
#define 	RX_PHY_ENCODING			r13
#define 	SHORT_RETRY_LIMIT		r14
#define 	SHORT_RETRIES			r15
#define 	LONG_RETRIES			r16
#define 	SEQUENCE_CTR			r17
#define 	PROBE_REQ_RING_START_PTR	r18
#define 	PROBE_REQ_RING_END_PTR		r19
#define 	MEASURED_PROBE_REQ_CTR		r20
#define 	CURRENT_DTIM_COUNT		r21
#define 	ANTENNA_DIVERSITY_CTR		r22
#define 	GPHY_SYM_WAR_FLAG		r23
#define 	EXPECTED_CTL_RESPONSE		r24
#define 	NEXT_TXE0_CTL			r25

#define 	GP_REG0			r27
#define 	GP_REG1			r28
#define 	GP_REG2			r29
#define 	GP_REG3			r30		
#define 	GP_REG5			r32		
#define 	GP_REG6			r33		
#define 	GP_REG7			r34		
#define 	GP_REG8			r35		
#define 	GP_REG9			r36		
#define 	GP_REG10		r37		

// ********
// ATTENZIONE ad usa re GP_REG11 insieme con CONVENIENCE_2 perchè sono la stessa cosa
#define 	GP_REG11		r38
#define		CONVENIENCE		r38

// ********
// ATTENZIONE ad usa re GP_REG12 insieme con CONVENIENCE perchè sono la stessa cosa
#define		GP_REG12		r39	
#define		CONVENIENCE_2		r39



#define		WATCHDOG		r1

#define		NEXT_IFS		r40
#define		NEXT_CONTENTION_WIN	r41
#define		UNANSWERED_PROBE_REQ_CTR	r42	

#define		NEAR_SLOT		r43
#define		COUNT_SLOT		r44
// 0x001F: number of current slot
// 0x1000: start slot detected; 
// 0x2000: microwave noise end detected;

//defenid before (at start of the this file)
;//#define 	GLOBAL_FLAGS_REG2		r45

#define		SINC_SLOT_0		r46	
#define		SINC_SLOT_1		r47
#define 	SINC_SLOT_2		r48


#define		STATE_DEBUG_02		r49
#define		STATE_DEBUG_03		r50
#define		STATE_DEBUG_04		r51


#define 	REGION_DEBUG_START	0x0580
#define 	REGION_DEBUG_STOP 	0x07F0


#define 	COUNT_BAD_SLOT_0 r63
#define 	COUNT_BAD_SLOT_1 r62
#define 	COUNT_BAD_SLOT_2 r61
#define 	COUNT_BAD_SLOT_3 r60
#define 	COUNT_BAD_SLOT_4 r59
#define 	COUNT_BAD_SLOT_5 r58
#define 	COUNT_BAD_SLOT_6 r57
#define 	COUNT_BAD_SLOT_7 r56
#define 	COUNT_BAD_SLOT_8 r55
#define 	COUNT_BAD_SLOT_9 r54

#define		COUNT_BAD_SLOT_CURRENT r53
#define		COUNT_GOOD_SLOT_CURRENT r52

/* Params definitions */

#define		SHM_FIFO_RDY		0x16E	
